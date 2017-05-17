# -*- coding: UTF-8 -*- 
#!/usr/bin/python3
import os
import lib_new.InputIQ as InputIQ
import lib_new.NCO as NCO
import lib_new.CACodeGen as CACodeGen
import lib_new.NewSearch as NewSearch
import lib_new.Tracker as Tracker
import lib_new.BitSync as BitSync
import lib_new.FrameSync as FrameSync
import numpy
import pyfftw
import math
import matplotlib.pyplot as plt

class Main(object):
    """docstring for Main"""
    def __init__(self, IQ_input1, IQ_input2,code_td,prn=3):
        super(Main, self).__init__()
        self.prn = prn
        self.adc_sample_freq = 15.625e6 
        self.ca_code_freq = 1.023e6
        self.inter_freq = 4.1309375e6
        self.sample_period = 1e-3 # 1ms
        self.num_samples = 10 * int(self.adc_sample_freq * self.sample_period)
        self.IQ_input1 = IQ_input1
        self.IQ_input2 = IQ_input2
        self.code_nco_len = 32
        self.carrier_nco_len = 32
        self.code_td = code_td
        
    def process(self):
        search_process1 = NewSearch.NewSearch(self.prn,self.IQ_input1)
        search_process2 = NewSearch.NewSearch(self.prn,self.IQ_input2)

        # self.IQ_input1.reset()
        input_iq1, input_time1 = self.IQ_input1.read(1000)
        # self.IQ_input2.reset()
        input_iq2, input_time2 =self.IQ_input2.read(1000)

        distance = int((input_time1[0]-input_time2[0]) / 64)
        # print(distance)

        if distance < 0:
            input_iq1, input_time1 = self.IQ_input1.read(abs(distance))
        else:
            input_iq2, input_time2 = self.IQ_input2.read(abs(distance))

        self.IQ_input1.read(self.num_samples*6)
        self.IQ_input2.read(self.num_samples*6)

        find1, snr_max1, dop_freq1, peak_shift1 = search_process1.process()
        find2, snr_max2, dop_freq2, peak_shift2 = search_process2.process()        
        
        peak_shift = int((peak_shift1+peak_shift2)/2)

        self.IQ_input1.read(peak_shift)
        self.IQ_input2.read(peak_shift)

        input_iq1, input_time1 = self.IQ_input1.read(self.num_samples)
        input_iq2, input_time2 = self.IQ_input2.read(self.num_samples)

        mix_td1 = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        mix_td2 = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        
        input_td1 = numpy.array(input_iq1)
        input_td2 = numpy.array(input_iq2)

        mix_td1_real_list=[]
        mix_td1_imag_list=[]
        mix_td2_real_list=[]
        mix_td2_imag_list=[]

          
        carrier_nco1 = NCO.NCO(self.carrier_nco_len,0,self.adc_sample_freq,self.inter_freq+dop_freq1)
        carrier_nco2 = NCO.NCO(self.carrier_nco_len,0,self.adc_sample_freq,self.inter_freq+dop_freq2)

        carrier1 = []
        carrier2 = []

        for i in range(self.num_samples):
            carrier_sin1, carrier_cos1 = carrier_nco1.getSinCos()
            carrier1.append(complex(carrier_cos1,carrier_sin1))
            # mix the input signal with local carrier
            carrier_nco1.tick()
            carrier_sin2, carrier_cos2 = carrier_nco2.getSinCos()
            carrier2.append(complex(carrier_cos2,carrier_sin2))
            # mix the input signal with local carrier
            carrier_nco2.tick()

        for i in range(self.num_samples):
            mix_td1[i] = numpy.conj(carrier1[i]) * input_td1[i] * self.code_td[i]
            mix_td2[i] = numpy.conj(carrier2[i]) * input_td2[i] * self.code_td[i]

        sum_Prompt1 = mix_td1.sum()
        sum_Prompt2 = mix_td2.sum()
        pll_err1 = math.atan(sum_Prompt1.imag/sum_Prompt1.real)
        pll_err2 = math.atan(sum_Prompt2.imag/sum_Prompt2.real)
    
        print(abs(mix_td1.sum()))
        print(abs(mix_td2.sum()))
        print(pll_err1-pll_err2)

        # if (not find):
        #     print("Try another prn!\n")
        # else:
        #     self.IQ_input.reset()
        #     self.IQ_input.read(int(peak_shift)-15)
        #     tracker_process = Tracker.Tracker(self.prn,dop_freq,self.IQ_input)
        #     bit_sync = BitSync.BitSync()
        #     bit_count = 0
        #     frame_sync = FrameSync.FrameSync()
        #     frame_count = 0
        #     frame_sync_count=0
        #     while True:
        #         bit, pll_error, dll_error = tracker_process.process(phase_file)
        #         sync_bit = bit_sync.process(bit)
        #         bit_count += 1
        #         if (sync_bit):
        #             print(bit_count,bit,sync_bit,pll_error,dll_error)
        #             fp_phase.write(str(bit_count))
        #             fp_phase.write(" ")
        #             fp_phase.write(str(bit))
        #             fp_phase.write(" ")
        #             fp_phase.write(str(sync_bit))
        #             fp_phase.write(" ")
        #             fp_phase.write(str(pll_error))
        #             fp_phase.write(" ")
        #             fp_phase.write(str(dll_error))
        #             fp_phase.write("\n")
        #             frame_sign = frame_sync.process(sync_bit)
        #             if abs(frame_sign) == 8:
        #                 print("frame sync!")
        #                 if frame_sign>0:
        #                     print("phase normal!\n")
        #                     fp_phase.write("phase normal!\n")
        #                     fp_phase.flush()
        #                 else:
        #                     print("phase inverted!\n")
        #                     fp_phase.write("phase inverted!\n")
        #                     fp_phase.flush()
        #                 frame_sync_count+=1
        #                 if frame_sync_count==4:
        #                     break
        #             else:
        #                 frame_count += 1


def main():
    ip1 = "192.168.0.2"
    ip2 = "192.168.0.4"
    num_list = ["test0"]
    # num_list = ["test0","test1","test2","test3","test4","test5",
    # "test6","test7","test8","test9","testa"]

    prn = 5
    adc_sample_freq = 15.625e6 
    ca_code_freq = 1.023e6
    inter_freq = 4.1309375e6
    sample_period = 1e-3 # 1ms
    num_samples = 10*int(adc_sample_freq * sample_period)
    code_nco_len = 32
    carrier_nco_len = 32
    # Create local code replicas for each frequency bin.
    code_index = 0
    code_gen = CACodeGen.CACodeGen(prn)
    code_nco = NCO.NCO(code_nco_len,0,adc_sample_freq,ca_code_freq)
    code_td  = pyfftw.empty_aligned(num_samples, dtype='complex128')
    update = False

    for i in range(num_samples):
        code = code_gen.getCode(code_index)
        code_td[i] = complex(code,0)
        update, code_phase = code_nco.tick()
        if (update):
            code_index+=1

    for num in num_list:
        IQ_input1 = InputIQ.InputIQ("../../new_raw/gps_adc_"+ip1+num)
        IQ_input2 = InputIQ.InputIQ("../../new_raw/gps_adc_"+ip2+num)
        print(num)
        start = Main(IQ_input1,IQ_input2,code_td,prn)
        start.process()

if __name__ == '__main__':
    main()
