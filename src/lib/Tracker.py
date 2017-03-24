#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import CACodeGenerator
import CCReplica
import GNSSconstants
import InputIQ
import datetime
import sys

class Tracker(object):
    """docstring for Tracker"""

    def __init__(self, prn, dop_freq):
        super(Tracker, self).__init__()
        
        self.adc_amplitude = GNSSconstants.GNSSconstants.ADC_AMPLITUDE
        self.adc_sample_freq = GNSSconstants.GNSSconstants.L1_FREQ_ADC_SAMPLE
        self.chip_freq = GNSSconstants.GNSSconstants.CA_CHIP_FREQ_GPS
        self.inter_freq = GNSSconstants.GNSSconstants.L1_INTER_GPS
        self.sample_period = GNSSconstants.GNSSconstants.SAMPLE_PERIOD
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        # page 356, the maximum Doppler frequency offset is +-10kHz
        self.freqSearchWidth = 20000 
        self.freqBinWidth = 200 
        self.bins = (20000 // 200 + 1)
        # the period of C/A code is 1ms
        self.numSamples = int(self.adc_sample_freq * self.sample_period)
        self.prn = prn
        self.peak = 0.008
        self.PrnCACodeGen = CACodeGenerator.CACodeGenerator(self.prn)
        self.PrnCCGen = CCReplica.CCReplica(self.adc_sample_freq,self.chip_freq,
                          self.inter_freq+dop_freq,self.PrnCACodeGen)
        self.PrnCCGen.reset(0)
        self.iad_threshold = 130
        self.dll_mode = 0 # code loop
        self.search_size = 0.5
        self.pll_mode = 0 # carrier loop
        self.dll_alpha = 0.1
        self.pll_p = 0.3
        self.pll_i = 0.025
        self.pll_error_prev = 0
        # self.dll_beta = 0.005

    def process(self,shift,times):
        
        # Get input code
        IQ_input = InputIQ.InputIQ("gps_adc.txt")

        prn_code_early = pyfftw.zeros_aligned(self.numSamples, dtype='complex128')
        prn_code_prompt = pyfftw.zeros_aligned(self.numSamples, dtype='complex128')
        prn_code_late = pyfftw.zeros_aligned(self.numSamples, dtype='complex128')
        multi_in = pyfftw.zeros_aligned(self.numSamples, dtype='complex128')

        a=[]
        b=[]
        c=[]
        d=[]
        e=[]
        f=[]
        
        for i in range(times):
            input_td = numpy.array(IQ_input.read(self.num_samples))

        code_phase_complete=0
        carrier_phase_complete=0
        
        code_phase = 0
        carrier_phase = 0

        self.PrnCCGen.reset(0)
        for j in range(self.numSamples):
            carrier = self.PrnCCGen.getCarrier()
            # mix in the carrier local replica
            multi_in[j] = numpy.conj(carrier) * input_td[j]
            self.PrnCCGen.tick()

        while (not code_phase_complete):
            self.PrnCCGen.reset(0)
            self.PrnCCGen.moveCodePhase(shift/self.adc_sample_freq*self.chip_freq)
            self.PrnCCGen.moveCodePhase(code_phase)
        
            for j in range(self.numSamples):
                prn_code_early[j] = complex(self.PrnCCGen.getCodeEarly(),0)
                prn_code_prompt[j] = complex(self.PrnCCGen.getCodePrompt(),0)
                prn_code_late[j] = complex(self.PrnCCGen.getCodeLate(),0)
                self.PrnCCGen.tick()

            sum_code_early = sum(prn_code_early * multi_in)
            sum_code_prompt = sum(prn_code_prompt * multi_in)
            sum_code_late = sum(prn_code_late * multi_in)
            
            emag = abs(sum_code_early)
            pmag = abs(sum_code_prompt)
            lmag = abs(sum_code_late)

            dll_error = 0.5 * (emag - lmag) / (emag + lmag)

            if ( (pmag > self.iad_threshold) and (pmag > max(emag,lmag)) ):
               dll_mode = 3 # on_top
            elif (pmag<min(emag,lmag)):
                dll_mode = 1
            elif ( (emag > self.iad_threshold) or (pmag > self.iad_threshold) or (lmag > self.iad_threshold) ):
               dll_mode = 2 # dm_close
            else:
               dll_mode = 1 # dm_far

            # Close the loop on the dll
            if ( (dll_mode == 3)  or (dll_mode == 2) ): # on_top or dm_close
               # PI control
               code_phase += self.dll_alpha * dll_error
            else:
               code_phase += self.search_size
            
            # a.append(emag)
            # b.append(pmag)
            # c.append(lmag)
            # d.append(dll_error)

            print(emag,pmag,lmag,code_phase,dll_error,dll_mode)

            if dll_error<0.02 and dll_mode==3:
                code_phase_complete=1

        while (not carrier_phase_complete):
            self.PrnCCGen.reset(0)
            carrier_phase = carrier_phase + 0.015
            self.PrnCCGen.moveCarrierPhase(carrier_phase)
            for j in range(self.numSamples):
                carrier = self.PrnCCGen.getCarrier()
                # mix in the carrier local replica
                multi_in[j] = numpy.conj(carrier) * input_td[j]
                self.PrnCCGen.tick()

            sum_code_prompt = sum(prn_code_prompt * multi_in)

            I_P = sum_code_prompt.real
            Q_P = sum_code_prompt.imag
            # pll_error = math.atan(Q_P /I_P) / GNSSconstants.GNSSconstants.PI;
            # if abs(pll_error)<0.01:
            
            if abs(Q_P/I_P) < 0.05:
                carrier_phase_complete = 1

            # if abs(Q_P/I_P)<0.1:
            # print(Q_P/I_P)

            # print(I_P,Q_P,pll_error)
            # e.append(I_P)
            # f.append(Q_P)
            # self.PrnCCGen.moveCodePhase(code_phase)

            # # Close up the pll
            # if (dll_mode == 3): # on_top
            #     self.PrnCCGen.moveCarrierPhase(self.pll_p * pll_error+self.pll_d*(pll_error-self.pll_error_prev))
            #     self.PrnCCGen.carrier_freq_offset += self.pll_i * pll_error/self.num_samples

            # self.pll_error_prev = pll_error

            # if ((dll_mode == 3) and (abs(pll_error) < 0.3)):
            #     pll_mode = 1 # Locked
            # else:
            #     pll_mode = 0 # Unlocked


            # print(pll_mode, pll_error,self.PrnCCGen.carrier_phase)
            # if (pll_mode == 0 and dll_mode==3):
            #     e.append(tmp)
            # print(I_P,Q_P)
            # print(pll_error)
        print(pmag,code_phase,carrier_phase)
        # plt.subplot(4,1,1)
        # plt.plot(a)
        # plt.subplot(4,1,2)
        # plt.plot(b)   
        # plt.subplot(4,1,3)
        # plt.plot(c)
        # plt.subplot(4,1,4)
        # plt.plot(d)
        # plt.figure()
        # plt.subplot(2,1,1)
        # plt.plot(e)
        # plt.subplot(2,1,2)
        # plt.plot(f)
        # plt.show()
        return (code_phase,carrier_phase)
def main():
    acquire = Tracker(3,4897)
    fp = open("result.txt","w")
    times=0
    a=[]
    b=[]
    try:
        while True:
            times+=1
            code_phase,carrier_phase = acquire.process(9450,times)
            fp.write(str(times)+str(code_phase)+str(carrier_phase))
            a.append(code_phase)
            b.append(carrier_phase)
    except Exception as e:
        raise e
    finally:
        fp.close()
        plt.subplot(2,1,1)
        plt.plot(a)
        plt.subplot(2,1,2)
        plt.plot(b)
        plt.show()
        
    

if __name__ == '__main__':
    main()
