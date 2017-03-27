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

    def read(self,size):
        LIST=[]
        for i in range(size):
            QI = self.file.read(1)
            # if QI == "":
                # return -1
            Q_BIN=bin((int(QI,16)&0b1100)>>2)
            I_BIN=bin(int(QI,16)&0b0011)
            LIST.append(complex(data_format[I_BIN],data_format[Q_BIN]))
        return LIST

def main():
    n = 2**18
    n2= n/2
    IQ_input = InputIQ("../gps_adc.txt")
    Fs = 125e6/8
    Ts = 1.0 / Fs
    t = numpy.arange(0,1,Ts)
    k = numpy.arange(n)
    T= n / Fs
    frq_2 = k / T
    frq_1 = frq_2[:n2] # one side frequency range
    IQ_input.read(n)
    print(len(IQ_input.I_LIST))
    start=datetime.datetime.now()
    Y = numpy.fft.fft(IQ_input.Q_LIST)/n
    end=datetime.datetime.now()
    print(end-start)
    fig, ax = plt.subplots(1,2)
    print(len(abs(Y)),len(frq_2))
    ax[0].plot(frq_1,abs(Y[:n2]),'r')
    ax[1].plot(frq_2,abs(Y),'r')
    plt.show()

if __name__ == '__main__':
    main()