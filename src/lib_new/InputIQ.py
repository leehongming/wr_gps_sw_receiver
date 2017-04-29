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
        self.ns_time = 0
        self.s_time = 0

    def read(self,size):
        LIST=[]
        for i in range(size):
            if self.loc%1044 == 0:
                ip = self.file.read(2)
                tai = self.file.read(10)
                cycles = self.file.read(7)
                self.file.read(1)
                self.loc +=20
                tmp_ns = int(cycles,16)*8
                tmp_s = int(tai,16)
                period = (tmp_s-self.s_time)*1e9 + (tmp_ns - self.ns_time)
                self.ns_time = tmp_ns
                self.s_time = tmp_s
                if period!=65536:
                    print(period,)
            
            QI = self.file.read(1)
            self.loc += 1
            # if QI == "":
                # return -1
            Q_BIN=bin((int(QI,16)&0b1100)>>2)
            I_BIN=bin(int(QI,16)&0b0011)
            LIST.append(complex(data_format[I_BIN],data_format[Q_BIN]))
        return LIST
    
    def reset(self,loc=0):
        self.file.seek(loc)
        self.loc = loc

    def __del__(self):
        self.file.close()

def main():
    IQ_input = InputIQ("../data/gps_adc_192.168.0.2")
    IQ_input.read(254000)
    IQ_input.reset()
    IQ_input.read(254000)

if __name__ == '__main__':
    main()