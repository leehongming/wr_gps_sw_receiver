#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import CACodeGen
import ShiftReg
import InputIQ
import datetime
import sys
import NCO
import ShiftReg

class Tracker(object):
    """docstring for Tracker"""
    def __init__(self, prn, dop_freq, InputIQ):
        super(Tracker, self).__init__()
        self.adc_sample_freq = 15.625e6 
        self.ca_code_freq = 1.023e6
        self.inter_freq = 4.1309375e6
        # odd values recommended because of possible NAV change.
        self.sample_period = 1e-3 # 1ms
        # the period of C/A code is 1ms
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        # page 356, the maximum Doppler frequency offset is +-10kHz
        self.prn = prn
        self.code_index = 0
        self.code_gen = CACodeGen.CACodeGen(self.prn)
        self.code_nco_len = 8
        # The NCO freq is 2*ca_code_freq
        self.code_nco = NCO.NCO(self.code_nco_len,0,self.adc_sample_freq,self.ca_code_freq*2)
        self.carrier_nco_len = 4
        self.carrier_nco = NCO.NCO(self.carrier_nco_len,0,self.adc_sample_freq,self.inter_freq+dop_freq)
        self.IQ_input = InputIQ
        self.shift_reg = ShiftReg.ShiftReg(
                        self.code_gen.getCode(self.code_index),
                        self.code_gen.getCode(self.code_index-1),
                        self.code_gen.getCode(self.code_index-1))
        self.code_tick = 0.0
        self.code_incr = 0.0
        self.carrier_incr = 0.0
        self.carrier_incr_sum = 0.0
        self.carrier_incr_prev = 0.0
        self.dll_error = 1.0
        self.pll_error = 0.0
        self.pll_error_prev = 0.0
        self.mag_Early = 0.0
        self.mag_Late = 0.0
        self.dll_update = 0
        # self.a=[]
        # self.b=[]
        # self.c=[]

    def process(self):
        # Get input code
        input_td = numpy.array(self.IQ_input.read(self.num_samples))

        self.carrier_nco.ModifyPhaseIncr(self.carrier_incr)
        
        mix_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        for i in range(self.num_samples):
            carrier_sin, carrier_cos = self.carrier_nco.getPhase()
            carrier = complex(carrier_cos,carrier_sin)
            # mix the input signal with local carrier
            mix_td[i] = numpy.conj(carrier) * input_td[i]
            self.carrier_nco.tick()
        
        code = self.code_gen.getCode(self.code_index)
        Early = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        Prompt = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        Late = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        
        for i in range(self.num_samples):
            Early[i] = complex(self.shift_reg.reg1,0) * mix_td[i]
            Prompt[i]= complex(self.shift_reg.reg2,0) * mix_td[i]
            Late[i]  = complex(self.shift_reg.reg3,0) * mix_td[i]

            if (self.code_nco.tick()[0]):
                self.code_tick += 1
                if self.code_tick == 2:
                    self.code_index += 1
                    code = self.code_gen.getCode(self.code_index)
                    self.shift_reg.shift(code)
                    self.code_tick = 0
                else:
                    self.shift_reg.shift(code)

        sum_Early = Early.sum()
        sum_Prompt = Prompt.sum()
        sum_Late = Late.sum()

        self.mag_Early += abs(sum_Early)
        self.mag_Late += abs(sum_Late)
        mag_Prompt = abs(sum_Prompt)

        self.dll_error = 0.5 * (self.mag_Early - self.mag_Late) / (self.mag_Early + self.mag_Late)
        self.pll_error = math.atan(sum_Prompt.imag/sum_Prompt.real) / math.pi

        Tracker.carrier_loop_filter(self)
        self.carrier_incr_sum += self.carrier_incr
        self.dll_update += 1
        if self.dll_update==10:            
            self.code_incr = Tracker.code_loop_filter(self) + 1/1540 * self.carrier_incr_sum
            self.code_nco.ModifyPhaseIncr(self.code_incr)
            self.mag_Early = 0
            self.mag_Late = 0
            self.dll_update = 0
            self.carrier_incr_sum = 0

        # fp = open("pll_error","a+")
        # fp.write(str(self.pll_error)+"\n")
        # if(abs(self.pll_error)>0.1):
        #     print(self.pll_error,self.carrier_incr)
        # self.a.append(abs(sum_Prompt.imag))
        # self.b.append(abs(sum_Prompt.real)) 
        # print(self.dll_error,self.pll_error)
        # self.a.append(self.dll_error)
        # self.c.append(self.pll_error)
        # self.a.append(self.mag_Early)
        # self.b.append(mag_Prompt)
        # self.c.append(self.mag_Late)

        if abs(self.pll_error) < 0.25 and abs(self.dll_error) < 0.3:
            return 1 if sum_Prompt.real>0 else -1
        else:
            print("Unlock!\n")
            return 0

    def carrier_loop_filter(self):
        # Two order low pass filter, BL= 15Hz, page 273
        a2 = 1.414
        wn = 28.3
        K1 = self.num_samples
        K2 = 4
        self.carrier_incr = self.carrier_incr_prev + \
                (a2*wn+(wn**2)/2/1e3)*self.pll_error/K1/K2  + \
                (-a2*wn+(wn**2)/2/1e3)*self.pll_error_prev/K1/K2
                # (a2*wn)*self.pll_error/K1/K2  + \
                # (-a2*wn)*self.pll_error_prev/K1/K2
        self.pll_error_prev = self.pll_error
        self.carrier_incr_prev = self.carrier_incr
        return

    def code_loop_filter(self):
        wn = 20
        K = self.num_samples
        code_incr = wn * self.dll_error / K
        return code_incr

def main():
    fp_data = open("data.txt","w+")
    data=[]
    IQ_input = InputIQ.InputIQ("../gps_adc.txt")
    a = Tracker(3,5400,IQ_input)
    a.IQ_input.read(6115)
    for i in range(7000):
        bit = a.process()
        data.append(bit)
        fp_data.write(str(bit)+"\n")
    # plt.subplot(3,1,1)
    # plt.plot(a.a)
    # plt.subplot(3,1,2)
    # plt.plot(a.b)
    # plt.subplot(3,1,3)
    # plt.plot(a.c)
    # plt.show()

if __name__ == '__main__':
    main()
