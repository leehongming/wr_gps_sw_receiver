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

    def read(self,size):
        LIST=[]
        self.loc += size
        for i in range(size):
            QI = self.file.read(1)
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
    IQ_input = InputIQ("../gps_adc.txt")
    print(IQ_input.read(10))
    print(IQ_input.reset())
    print(IQ_input.read(10))
    print(IQ_input.read(10))

if __name__ == '__main__':
    main()