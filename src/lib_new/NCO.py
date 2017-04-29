#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

import math
import numpy
import matplotlib.pyplot as plt

class NCO(object):
    """docstring for NCO"""
    def __init__(self, reg_len ,reg_init, clock_freq, nco_freq):
        super(NCO, self).__init__()
        self.reg_max = 2 ** reg_len
        self.reg = reg_init
        self.phase_incr_center = round(nco_freq / clock_freq * (2 ** reg_len))
        self.phase_incr = self.phase_incr_center
        
    def getSinCos(self):
        phase = 2 * math.pi * self.reg / self.reg_max
        return (math.sin(phase), math.cos(phase))

    def getPhase(self):
        phase = 2 * math.pi * self.reg / self.reg_max
        return phase

    def tick(self):
        self.reg += self.phase_incr
        if self.reg >= self.reg_max:
            self.reg -= self.reg_max
            return (True, self.reg/self.phase_incr)
        else:
            return (False, 0)

    def ModifyPhaseIncr(self,M):
        self.phase_incr = self.phase_incr_center + M

def main():
    a = NCO(10,0,10e6,10e4)
    sin_list = []
    cos_list = []
    print(a.phase_incr)
    a.ModifyPhaseIncr(0)

    for i in range(1000):
        sin, cos = a.getSinCos()
        a.tick()
        sin_list.append(sin)
        cos_list.append(cos)

    plt.subplot(2,1,1)
    plt.plot(sin_list)
    plt.subplot(2,1,2)
    plt.plot(cos_list)
    plt.show()

if __name__ == '__main__':
    main()