#!/usr/bin/python3
# -*- coding: UTF-8 -*-

from CodeGenerator import *
import MSequence 
import numpy
import matplotlib.pyplot as plt

class CACodeGenerator(CodeGenerator):
    """Generate the CA code. Init with the PRN num. """
    
    # G1 = 1 + x^3 + x^10
    G1_Initial_Vector=0x3FF
    G1_Polynomial=(1<<10)|(1<<3)
    # G2 = 1 + x^2 + x^3 + x^6 + x^8 + x^9 + x^10
    G2_Initial_Vector=0x3FF
    G2_Polynomial=(1<<10)|(1<<9)|(1<<8)|(1<<6)|(1<<3)|(1<<2)
    # Length of CA code
    CA_code_len = 1023;

    def __init__(self,prn):
        self.G1 = MSequence.MSequence(CACodeGenerator.CA_code_len,
            CACodeGenerator.G1_Initial_Vector,CACodeGenerator.G1_Polynomial)
        self.G2 = MSequence.MSequence(CACodeGenerator.CA_code_len,
            CACodeGenerator.G2_Initial_Vector,CACodeGenerator.G2_Polynomial)
        self.prn = prn
        self.chip_count = 0
        self.setIndex(0)

    def popup(self):
        self.chip_count+=1
        self.G1.popup()
        self.G2.popup()
        return

    def getCode(self):
        return (self.G1.getValue() ^ self.G2.getValue())

    def setIndex(self,new_index):
        self.G1.setIndex(new_index)
        self.G2.setIndex(new_index+CACodeGenerator.CA_code_len-CACodeGenerator.getG2Delay(self.prn))

    def getIndex(self):
        return self.G1.getIndex()

    def isLastInSequence(self):
        return (self.G1.isLastInSequence())

    def getSyncIndex(self):
        return CACodeGenerator.CA_code_len

    def getChipCount(self):
        return self.chip_count

    def reset(self):
        self.setIndex(0)
        self.chip_count = 0

    def getG2Delay(prn):
       G2DelayTable=(0,5,6,7,8,17,18,139,140,141,251,252,254,255,256,
          257,258,469,470,471,472,473,474,509,512,513,514,
          515,516,859,860,861,862,863,950,947,948,950)
       return G2DelayTable[prn];

def correlate(lista,listb):
    n = len(lista)
    series_a = numpy.asarray(lista)

    def r(h):
        series_b = numpy.roll(listb,h) #  ring shift left
        acf_lag = (series_a*series_b).sum()/float(n)
        return acf_lag
    left_shift = -round(CACodeGenerator.CA_code_len/2)
    right_shift = round(CACodeGenerator.CA_code_len/2)
    x = numpy.arange(left_shift,right_shift)
    # acf_coeffs = map(r, x)
    acf_coeffs = [r(i) for i in x]
    return acf_coeffs

def main():
    # CA code generator example
    CAGen = CACodeGenerator(1)
    CAGen2 = CACodeGenerator(2)
    a= 0x0000
    for i in range(1023):
        a = (a<<1) + (CAGen.getCode())
        CAGen.popup()
    
    print(oct(a))
    print(CAGen.getIndex())
    print(CAGen.isLastInSequence())
    print(CAGen.getSyncIndex())
    print(CAGen.getChipCount())
    print(CAGen.reset())

    lista=[]
    listb=[]
    for i in range(CACodeGenerator.CA_code_len*10):
        code = 1 if CAGen.getCode() else -1        
        lista.append(code)
        CAGen.popup()

    for i in range(CACodeGenerator.CA_code_len*10):
        code = 1 if CAGen2.getCode() else -1        
        listb.append(1)
        CAGen2.popup()
    
    plt.plot(correlate(lista,lista))
    # plt.plot(correlate(lista,listb))
    plt.show()

if __name__ == '__main__':
    main()