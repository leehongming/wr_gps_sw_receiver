#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

import math
import numpy

class ParityCheck(object):
    """docstring for ParityCheck"""
    def __init__(self):
        super(ParityCheck, self).__init__()

        self.H = numpy.mat(
            [ [1,0,1,1,1,0,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,0],
              [0,1,0,1,1,1,0,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1],
              [1,0,1,0,1,1,1,0,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0],
              [0,1,0,1,0,1,1,1,0,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0],
              [0,1,1,0,1,0,1,1,1,0,1,1,0,0,0,1,1,1,1,1,0,0,1,1,0,1],
              [1,0,0,0,1,0,1,1,0,1,1,1,1,0,1,0,1,0,0,0,1,0,0,1,1,1]
            ])


def main():
    pc = ParityCheck()
    a = [1,0,0,0,1,0,1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,1,0,0]
    b = [0^i for i in a]
    r=numpy.mat([0,0,1,0,0,0,1,0,1,1,0,0,0,0,0,1,1,0,0,0,1,0,0,1,0,0])
    l=numpy.mat([1,0,0,0,0,1])
    
    result = pc.H*r.T
    l_check = [int(x)%2 for x in result ]
    check = l_check-l
    if(check.max() == 0):
        print("check pass!")


if __name__ == '__main__':
    main()

100111001101111101010001111000
