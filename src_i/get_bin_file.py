#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import datetime
import lib_new.CACodeGen as CACodeGen
import lib_new.NCO as NCO
import lib_new.InputIQ as InputIQ
import struct

class Search(object):
    """docstring for Search"""
    def __init__(self, prn, InputIQ1, InputIQ2):
        super(Search, self).__init__()
        self.adc_sample_freq = 15.625e6 
        self.ca_code_freq = 1.023e6
        self.inter_freq = 4.1309375e6
        # odd values recommended because of possible NAV change.
        self.sample_period = 1e-3 # 1ms
        # the period of C/A code is 1ms
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        # page 356, the maximum Doppler frequency offset is +-10kHz
        self.freqSearchWidth = 20000
        self.freqBinWidth = 200
        self.bins = (self.freqSearchWidth // self.freqBinWidth + 1)    
        self.prn = prn
        self.search_snr = 6.5
        self.IQ_input1 = InputIQ1
        self.IQ_input2 = InputIQ2

    def process(self,ip1,ip2,test_num):
        
        reset = 8000
        self.IQ_input1.reset(int(reset*self.num_samples//1250))
        self.IQ_input2.reset(int(reset*self.num_samples//1250))
        input_td1, input_time1 = self.IQ_input1.read(10)
        input_td2, input_time2 = self.IQ_input2.read(10)
        print("read file1\n")
        print("read file2\n")

        distance = int((input_time1[0]-input_time2[0]) / 64)

        if distance < 0:
            new_loc = abs(distance)//1250;
            self.IQ_input1.reset(new_loc+int(reset*self.num_samples//1250))
            remain = abs(distance) - new_loc * 1250 
            input_td1, input_time1 = self.IQ_input1.read(remain)
        else:
            new_loc = abs(distance)//1250;
            self.IQ_input1.reset(new_loc+int(reset*self.num_samples//1250))
            remain = abs(distance) - new_loc * 1250 
            input_td2, input_time2 = self.IQ_input2.read(remain)

        input_td1, input_time1 = self.IQ_input1.read(10)
        input_td2, input_time2 =self.IQ_input2.read(10)
        distance = int((input_time1[0]-input_time2[0]) / 64)

        if distance < 0:
            input_td1, input_time1 = self.IQ_input1.read(abs(distance))
        else:
            input_td2, input_time2 = self.IQ_input2.read(abs(distance))

        input_td1, input_time1 = self.IQ_input1.read(10)
        input_td2, input_time2 =self.IQ_input2.read(10)
        distance = int((input_time1[0]-input_time2[0]) / 64)
        
        print(distance)

        exp_num= "test21"
        if distance==0:
            f1=open('test'+ip1+exp_num+'.bin','ab')
            f2=open('test'+ip2+exp_num+'.bin','ab')    
            for j in range(300000):
                input_td1,input_time1 = self.IQ_input1.read(self.num_samples)
                input_td2,input_time2 = self.IQ_input2.read(self.num_samples)
                for i in range(self.num_samples):
                    f1.write(struct.pack('b',(input_td1[i])))
                    f2.write(struct.pack('b',(input_td2[i])))
                f1.flush()
                f2.flush()
                print(j,int((input_time1[0]-input_time2[0])))

def main():
    ip1 = "192.168.0.2"
    ip2 = "192.168.0.4"
    test_num = "test2"
    IQ_input1 = InputIQ.InputIQ("../../raw/gps_adc_"+ip1+test_num)
    IQ_input2 = InputIQ.InputIQ("../../raw/gps_adc_"+ip2+test_num)
    acquire = Search(5,IQ_input1,IQ_input2)
    acquire.process(ip1,ip2,test_num)
    
if __name__ == '__main__':
    main()
