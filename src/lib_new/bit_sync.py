#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import math
import numpy
import matplotlib.pyplot as plt

class BitSync(object):
    """docstring for BitSync"""
    def __init__(self):
        super(BitSync, self).__init__()
        self.bit_period = 20
        self.bit_reg = [0 for i in range(20)]
        self.bit_count = 0
        self.bit_prev = 0

    def process(self,bit):
        if (bit+self.bit_prev) == 0:
            self.count = 0
            self.bit_reg.pop(0)
            self.bit_reg.append(bit)
        elif bit == 0:
            self.count += 1
            self.bit_reg.append(bit_prev)
        else:
            self.count += 1
            self.bit_reg.append(bit)
            
def main():
    pass

if __name__ == '__main__':
    main()