# -*- coding: UTF-8 -*- 
#!/usr/bin/python3
import math
import matplotlib.pyplot as plt
import numpy

class BitSync(object):
    """docstring for BitSync"""
    def __init__(self):
        super(BitSync, self).__init__()
        self.bit_count = 0
        self.bit_len = 20
        self.bit_prev = 0
        self.bit_reg = [0 for i in range(20)]

    def process(self,bit):
        self.bit_reg.pop(0)
        self.bit_reg.append(bit)
        self.bit_count += 1

        if self.bit_count == self.bit_len:
            self.bit_count = 0
            bit_sum = sum(self.bit_reg)
            if bit_sum > self.bit_len-1:
                bit_o = 1
            elif bit_sum < -self.bit_len+1:
                bit_o = -1
            else:
                print("bit error!\n")
                bit_o = 0
        else:            
            bit_o = 0
            if (bit+self.bit_prev)==0:
                self.bit_count = 1

        self.bit_prev = bit

        if bit_o == 0:
            return None
        else:
            return bit_o

def main():
    file = open("data.txt","r")
    bit_sync = BitSync()

    for i in range(6011):
        tmp = bit_sync.process(int(file.readline().strip('\n')))
        if (tmp):
            print(i//20,tmp)

if __name__ == '__main__':
    main()