#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import datetime
import sys
import lib_new.CACodeGen as CACodeGen
import lib_new.ShiftReg as ShiftReg
import lib_new.InputIQ as InputIQ
import lib_new.NCO as NCO
import lib_new.ShiftReg as ShiftReg

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
        self.code_nco_len = 32
        # The NCO freq is 2*ca_code_freq
        self.code_nco = NCO.NCO(self.code_nco_len,0,self.adc_sample_freq,self.ca_code_freq*2)
        self.carrier_nco_len = 32
        self.carrier_nco = NCO.NCO(self.carrier_nco_len,0,self.adc_sample_freq,self.inter_freq+dop_freq)
        self.IQ_input = InputIQ
        self.shift_reg = ShiftReg.ShiftReg(
                        self.code_gen.getCode(self.code_index),
                        self.code_gen.getCode(self.code_index-1),
                        self.code_gen.getCode(self.code_index-1))
        self.code_tick = 0.0
        self.code_incr = 0
        self.carrier_incr = 0
        self.carrier_incr_sum = 0
        self.carrier_incr_prev = 0
        self.dll_error_meas = 0.0
        self.dll_error = 0.0
        self.pll_error = 0.0
        self.pll_error_prev = 0.0
        self.dll_update = 0
        self.mag_Early = 0.0
        self.mag_Late = 0.0
        self.init = 0
        self.b=[]
        self.c=[]

    def process(self):
        # Get input code
        input_iq, input_time = self.IQ_input.read(self.num_samples)
        input_td = numpy.array(input_iq)

        carrier_phase_list = []
        mix_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        for i in range(self.num_samples):
            carrier_sin, carrier_cos = self.carrier_nco.getSinCos()
            carrier_phase_list.append(self.carrier_nco.getPhase())
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
        self.carrier_nco.ModifyPhaseIncr(self.carrier_incr)
        # self.carrier_nco.ModifyPhaseIncr(14000)
        self.carrier_incr_sum += self.carrier_incr
        self.dll_error_meas = 0.5 * (self.mag_Early - self.mag_Late) / (self.mag_Early + self.mag_Late)

        if (self.dll_update >= 10):
            Tracker.code_loop_filter(self)
            self.code_nco.ModifyPhaseIncr(round(self.code_incr)+round(self.carrier_incr_sum/1540))
            self.carrier_incr_sum=0
            self.dll_update = 0
            self.mag_Early = 0
            self.mag_Late = 0
        else:
            self.dll_update += 1


        # if (self.dll_update == 0):
        #     Tracker.code_loop_filter(self)
        #     self.code_nco.ModifyPhaseIncr(round(self.code_incr))
        #     self.dll_update += 1
        # else:
        #     self.dll_update += 1
        #     if self.dll_update >= 1:
        #         self.dll_update = 0
        #         self.mag_Early = 0
        #         self.mag_Late = 0
        
        # fp = open("pll_error","a+")
        # fp.write(str(self.pll_error)+"\n")
        # if(abs(self.pll_error)>0.1):
        #     print(self.pll_error,self.carrier_incr)
        # self.a.append(mag_Prompt)
        # self.b.append(abs(sum_Prompt.imag))
        # self.a.append(abs(sum_Prompt.real)) 
        
        
        # self.a.append(self.mag_Early)
        # self.b.append(mag_Prompt)
        # self.b.append(abs(sum_Late))
        # self.c.append(self.pll_error)
        # self.c.append(self.dll_error)
        # self.c.append(mag_Prompt)
        # self.c.append(self.mag_Late)        

        if abs(self.pll_error) < 0.2 and abs(self.dll_error_meas) < 0.5:
            return (1 if sum_Prompt.real>0 else -1), self.pll_error, self.dll_error_meas, carrier_phase_list
        else:
            print(self.dll_error_meas,self.pll_error)
            return 0, self.pll_error, self.dll_error_meas, carrier_phase_list

    def carrier_loop_filter(self):
        # Two order low pass filter, BL= 15Hz, page 273
        a2 = 1.414
        wn = 28.3
        K = 2000 / 1.5
        if self.init==0:
            self.init+=1
        else:
            self.carrier_incr = self.carrier_incr_prev + \
                round ((a2*wn+(wn**2)/2/1e3)*self.pll_error*K  + \
                (-a2*wn+(wn**2)/2/1e3)*self.pll_error_prev*K )
        self.carrier_incr_prev = self.carrier_incr
        self.pll_error_prev = self.pll_error

        return

    def code_loop_filter(self):
        K = 30000
        self.dll_error = 0.65*self.dll_error+0.35*self.dll_error_meas
        self.code_incr=self.dll_error * K
        return 

def main():
    fp_data = open("data.txt","w+")
    data=[]

    # test3
    IQ_input = InputIQ.InputIQ("../../../cutewr_dp_gps/tools/gps_data/raw/gps_adc_192.168.0.2_test3") # test3
    a = Tracker(5,7400,IQ_input) # test3
    a.IQ_input.read(1181-3) # test3
    try:
        for i in range(20000):
            bit = a.process("../data/192.168.0.2_test3") # test3
            data.append(bit)
    # test5
    # IQ_input = InputIQ.InputIQ("../../../cutewr_dp_gps/tools/gps_data/raw/gps_adc_192.168.0.2_test4") # test4
    # a = Tracker(5,7400,IQ_input) # test4
    # a.IQ_input.read(7408) # test4
    # try:
    #     for i in range(20000):
            # bit = a.process("../data/192.168.0.2_test4") # test4
            # data.append(bit)

    # # test5
    # IQ_input = InputIQ.InputIQ("../../../cutewr_dp_gps/tools/gps_data/raw/gps_adc_192.168.0.2_test5")
    # a = Tracker(5,7400,IQ_input)
    # a.IQ_input.read(3990)
    # try:
    #     for i in range(20000):
    #         bit = a.process("../data/192.168.0.2_test5")
    #         data.append(bit)

    finally:
        print(max(a.c[30:]),min(a.c[30:]))
        # fp_data.write(str(a.c))
        plt.subplot(3,1,1)
        plt.plot(a.a[30:])
        plt.subplot(3,1,2)
        plt.plot(a.b[30:])
        plt.subplot(3,1,3)
        plt.plot(a.c[30:])
        plt.figure()
        plt.hist(a.c[30:])
        plt.show()

if __name__ == '__main__':
    main()
