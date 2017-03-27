# -*- coding: UTF-8 -*- 
#!/usr/bin/python3
import math
import matplotlib.pyplot as plt
import numpy
import BitSync

class FrameSync(object):
    """docstring for FrameSync"""
    def __init__(self):
        super(FrameSync, self).__init__()
        self.word_len = 30
        self.frame_len = 10
        self.sync_code_reg = [1,-1,-1,-1,1,-1,1,1]
        self.bit_reg = [0 for i in range(8)]
    
    def process(self,bit):
        self.bit_reg.pop(0)
        self.bit_reg.append(bit)
        sum_reg = sum([self.bit_reg[i] * self.sync_code_reg[i] for i in range(8)])
        return sum_reg

def main():
    file = open("data.txt","r")
    bit_sync = BitSync.BitSync()
    frame_sync = FrameSync()

    for i in range(6011):
        tmp = bit_sync.process(int(file.readline().strip('\n')))
        if (tmp):
            if abs(frame_sync.process(tmp)) == 8:
                print("frame sync!")
                print(i)


if __name__ == '__main__':
    main()