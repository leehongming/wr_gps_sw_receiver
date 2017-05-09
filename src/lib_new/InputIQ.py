#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

import numpy
import matplotlib.pyplot as plt
import datetime

data_format={
    '0b1':0.65/0.95,
    '0b0':0.20/0.95,
    '0b10':-0.20/0.95,
    '0b11':-0.65/0.95
}

class InputIQ(object):
    """docstring for InputIQ"""
    def __init__(self, filename):
        super(InputIQ, self).__init__()
        self.file = open(filename,"rb")
        self.loc = 0
        self.time = 0

    def read(self,size):
        LIST=[]
        TIME_LIST=[]
        for i in range(size):
            if self.loc%1040 == 0:
                self.file.read(1)
                tai = self.file.read(8)
                cycles = self.file.read(7)
                self.loc += 16
                tmp_ns = int(cycles,16)*8
                tmp_s = int(tai,16)
                period = tmp_s*1e9 + tmp_ns - self.time
                # if (period)!=64:
                #     print("Data lose!\n")
                self.time = tmp_s * 1e9 + tmp_ns - 64
            QI = self.file.read(1)
            self.loc += 1
            self.time +=  64
            Q_BIN=bin((int(QI,16)&0b1100)>>2)
            I_BIN=bin(int(QI,16)&0b0011)
            LIST.append(complex(data_format[I_BIN],data_format[Q_BIN]))
            TIME_LIST.append(self.time)
        return LIST, TIME_LIST
    
    def reset(self,loc=0):
        self.file.seek(loc)
        self.loc = loc
        self.time = 0

    def __del__(self):
        self.file.close()

def main():
    IQ_input = InputIQ("../data/gps_adc_192.168.0.2")
    IQ_input.read(254000)
    IQ_input.reset()
    IQ_input.read(254000)

if __name__ == '__main__':
    main()