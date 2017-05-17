#!/usr/bin/python3
# -*- coding: UTF-8 -*-

import numpy
import matplotlib.pyplot as plt

class ShiftReg(object):
    """Shift Reg """
    def __init__(self,reg1_init,reg2_init,reg3_init):
        self.reg1 = reg1_init
        self.reg2 = reg2_init
        self.reg3 = reg3_init

    def shift(self,reg):
        self.reg3 = self.reg2
        self.reg2 = self.reg1
        self.reg1 = reg

def main():
    A = ShiftReg(-1,-1,-1)
    for i in range(10):
        A.shift(1)
        print(A.reg1,A.reg2,A.reg3)

if __name__ == '__main__':
    main()