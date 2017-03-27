#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import MSequence 
import numpy
import matplotlib.pyplot as plt

class CACodeGen(object):
    """Generate CA code. Init with the PRN num. """
    # G1 = 1 + x^3 + x^10
    G1_Initial_Vector=0x3FF
    G1_Polynomial=(1<<10)|(1<<3)
    # G2 = 1 + x^2 + x^3 + x^6 + x^8 + x^9 + x^10
    G2_Initial_Vector=0x3FF
    G2_Polynomial=(1<<10)|(1<<9)|(1<<8)|(1<<6)|(1<<3)|(1<<2)
    # Length of CA code
    CA_code_len = 1023;

    def __init__(self,prn):
        self.G1 = MSequence.MSequence(CACodeGen.CA_code_len,
            CACodeGen.G1_Initial_Vector,CACodeGen.G1_Polynomial)
        self.G2 = MSequence.MSequence(CACodeGen.CA_code_len,
            CACodeGen.G2_Initial_Vector,CACodeGen.G2_Polynomial)
        self.prn = prn

    def getCode(self,index):
        self.G1.setIndex(index)
        self.G2.setIndex(index + CACodeGen.CA_code_len - CACodeGen.getG2Delay(self.prn))
        return (
            1.0 if self.G1.getValue() ^ self.G2.getValue() else
            -1.0
            )

    def isLastInSequence(self,index):
        return (index==CACodeGen.CA_code_len)

    def getG2Delay(prn):
       G2DelayTable=(0,5,6,7,8,17,18,139,140,141,251,252,254,255,256,
          257,258,469,470,471,472,473,474,509,512,513,514,
          515,516,859,860,861,862,863,950,947,948,950)
       return G2DelayTable[prn];

def main():
    CAGen = CACodeGen(3)
    a= 0x0000
    for i in range(10):
        a = (a<<1) + (CAGen.getCode(i))
    
    print(oct(a))

if __name__ == '__main__':
    main()