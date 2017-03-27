#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

import BitSet
import numpy as np

class MSequence(BitSet.BitSet):
    """docstring for MSequence"""

    def __init__(self, Length, Initial, Polynomial):
        # print("init MSequence")
        super(MSequence, self).__init__(Length)
        self.__start_index__ = 0
        self.__Length__ = Length
        self.__index__ = 0

        reg = Initial
        outputmask = 1
        temp = Polynomial >> 1
        # First compute outputmask by finding highest value bit in Polynomial 
        temp |= (temp >> 1);
        temp |= (temp >> 2);
        temp |= (temp >> 4);
        temp |= (temp >> 8);
        temp |= (temp >> 16);
        outputmask = temp ^ (temp >> 1);
        # Now compute the sequence 
        Polynomial_32 = np.int32(Polynomial)
        for i in range(self.__Length__):
            if (reg & 1):
                super(MSequence, self).set(i+self.__start_index__)
            else:
                super(MSequence, self).reset(i+self.__start_index__)
            accum = 0
            for j in range(32):
                if( Polynomial_32 & ( 1 << j ) ):  # WARNING: Assumes int is 32 bits 
                    accum = accum ^ (reg<<(j-1))
            reg=(reg>>1) | (accum & outputmask)

    def setIndex(self,new_index):
        self.__index__ = new_index % self.__Length__
        return self.getIndex()

    def getIndex(self):
        return self.__index__

    def isLastInSequence(self):
        return (self.__index__ == (self.__Length__-1))

    def popup(self):
        self.__index__ = (self.__index__+1) % self.__Length__
        return 

    def getValue(self):
        return super(MSequence, self).test(self.__index__)
        
def main():
    # CA code generator example
    G =  MSequence(1023,0x3F,(1<<5)|(1<<3))
    G1 = MSequence(1023,0x3FF,(1<<10)|(1<<3))
    G2 = MSequence(1023,0x3FF,(1<<10)|(1<<9)|(1<<8)|(1<<6)|(1<<3)|(1<<2))
    G2DelayTable = (0,5,6,7,8,17,18,139,140,141,251,252,254,255,256,
            257,258,469,470,471,472,473,474,509,512,513,514,
            515,516,859,860,861,862,863,950,947,948,950)
    
    G1.setIndex(0)
    G2.setIndex(0+1023-G2DelayTable[1])
    a=0x0000
    for i in range(10):
        a = (a<<1) + (G1.getValue() ^ G2.getValue())
        G1.popup()
        G2.popup()
    print(oct(a))

    for i in range(62):
        print(i,int(G.getValue()))
        G.popup()

if __name__ == '__main__':
    main()