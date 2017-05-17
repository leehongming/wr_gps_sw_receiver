# -*- coding: UTF-8 -*- 
#!/usr/bin/python3
import os
import lib_new.InputIQ as InputIQ
import lib_new.Search as Search
import lib_new.Tracker as Tracker
import lib_new.BitSync as BitSync
import lib_new.FrameSync as FrameSync
import numpy
import matplotlib.pyplot as plt
import math

class Main(object):
    """docstring for Main"""
    def __init__(self, IQ_input1, IQ_input2, prn=3):
        super(Main, self).__init__()
        self.prn = prn
        self.adc_sample_freq = 15.625e6 
        self.ca_code_freq = 1.023e6
        self.inter_freq = 4.1309375e6
        self.sample_period = 1e-3 # 1ms
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        self.IQ_input1 = IQ_input1
        self.IQ_input2 = IQ_input2
        self.code_nco_len = 32
        self.carrier_nco_len = 32
        self.IQ_input1 = IQ_input1
        self.IQ_input2 = IQ_input2
    
    def process(self,num):
        input_iq1, input_time1 = self.IQ_input1.read(100)
        input_iq2, input_time2 =self.IQ_input2.read(100)

        distance = int((input_time1[0]-input_time2[0]) / 64)
        if distance < 0:
            input_iq1, input_time1 = self.IQ_input1.read(abs(distance))
        else:
            input_iq2, input_time2 = self.IQ_input2.read(abs(distance))

        self.IQ_input1.read(self.num_samples*1)
        self.IQ_input2.read(self.num_samples*1)

        search_process1 = Search.Search(self.prn,self.IQ_input1)
        search_process2 = Search.Search(self.prn,self.IQ_input2)

        # fp_phase=open("../../new_raw_phase/"+num+"phase","w+")

        find1, snr_max1, dop_freq1, peak_shift1 = search_process1.process()
        find2, snr_max2, dop_freq2, peak_shift2 = search_process2.process()        

        tracker_process1 = Tracker.Tracker(self.prn,dop_freq1,self.IQ_input1)
        tracker_process2 = Tracker.Tracker(self.prn,dop_freq2,self.IQ_input2)

        peak_shift = int((peak_shift1+peak_shift2)/2)

        with open("../../phase/"+num,"a") as fp:
            if (find1 and find2):
                self.IQ_input1.read(peak_shift-8)
                self.IQ_input2.read(peak_shift-8)
                
                while True:
                    bit1, pll_error1, dll_error1, carrier_phase_list1 = tracker_process1.process()
                    bit2, pll_error2, dll_error2, carrier_phase_list2 = tracker_process2.process()

                    if bit1==0:
                        print("2 is tracking\n")
                    
                    if bit2==0:
                        print("4 is tracking\n")

                    if (bit1!=0) and (bit2!=0):
                        carrier_phase = numpy.array(carrier_phase_list1) - numpy.array(carrier_phase_list2)
                        for i in range(len(carrier_phase)):
                            if carrier_phase[i]<0:
                                carrier_phase[i]  += 2*math.pi 
                        mean= carrier_phase.mean()
                        std =carrier_phase.std()
                        print(mean,std)
                        fp.write(str(mean))
                        fp.write(":")
                        fp.write(str(std))
                        fp.write("\n")
            else:
                print("Try another prn!\n")

def main():
    ip1 = "192.168.0.2"
    ip2 = "192.168.0.4"
    num= "test0"

    IQ_input1 = InputIQ.InputIQ("../../new_raw/gps_adc_"+ip1+num)
    IQ_input2 = InputIQ.InputIQ("../../new_raw/gps_adc_"+ip2+num)
    start = Main(IQ_input1,IQ_input2,5)
    start.process(num)

if __name__ == '__main__':
    main()
