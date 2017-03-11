#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

from ConstLinearRecurrentSequence import *
from CodeGenerator import *

class CACodeGenerator(CodeGenerator):
    """docstring for CACodeGenerator"""

    G1_Initial_Vector=0x3FF;
    G2_Initial_Vector=0x3FF;

    G1_Polynomial=(1<<10)|(1<<3);
    G2_Polynomial=(1<<10)|(1<<9)|(1<<8)|(1<<6)|(1<<3)|(1<<2);
    
    CA_code_len = 1023;

    def __init__(self,prn):
        self.G1 = ConstLinearRecurrentSequence(CACodeGenerator.CA_code_len,
            CACodeGenerator.G1_Initial_Vector,CACodeGenerator.G1_Polynomial)
        self.G2 = ConstLinearRecurrentSequence(CACodeGenerator.CA_code_len,
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

    def getG2Delay(prn):
       G2DelayTable=(0,5,6,7,8,17,18,139,140,141,251,252,254,255,256,
          257,258,469,470,471,472,473,474,509,512,513,514,
          515,516,859,860,861,862,863,950,947,948,950)
       return G2DelayTable[prn];

def main():
    # CA code generator example
    CAG = CACodeGenerator(3)
    a= 0x0000
    for i in range(10):
        a = (a<<1) + (CAG.getCode())
        CAG.popup()
    print(oct(a))
    print(CAG.getIndex())
    print(CAG.isLastInSequence())
    print(CAG.getSyncIndex())
    print(CAG.getChipCount())
    print(CAG.reset())

if __name__ == '__main__':
    main()

