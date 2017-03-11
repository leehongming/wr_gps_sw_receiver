#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

from CACodeGenerator import *
from GNSSconstants import *
import ComplexMath
import matplotlib.pyplot as plt
import numpy as np

class CCReplica(object):
    """This is a intended to generate a local replica of a single code/carrier"""
       
    def __init__(self, tick_size, code_freq, carrier_freq, code_generator):
        super(CCReplica, self).__init__()
        self.tick_size = tick_size
        self.code_chiplen = 1.0/code_freq
        self.carrier_freq = carrier_freq
        self.chips_per_tick = tick_size * code_freq
        self.cycles_per_tick = tick_size * carrier_freq
        self.code_phase = 0
        self.code_phase_offset = 0
        self.code_freq_offset = 0
        self.carrier_phase = 0
        self.carrier_phase_offset = 0
        self.carrier_freq_offset = 0
        self.carrier_accum = 0
        self.local_time = 0
        self.code_generator = code_generator

    def getCode(self):
        return self.code_generator.getCode()

    def getCarrier(self): # value between -1 and 1
        return ComplexMath.sincos(2.0 * GNSSconstants.PI * self.carrier_phase)

    def wrapCode(self):
        if (self.code_phase<1):
            return
        if (self.code_phase<2):
            self.code_phase -= 1
            self.code_generator.popup()
        else:
            self.code_generator.setIndex(self.code_generator.getIndex() + self.code_phase)
            self.code_phase = 0

    def wrapCarrier(self):
        if (self.code_phase<1):
            return
        elif (self.code_phase<2):
            self.carrier_phase -=1
            self.carrier_accum +=1
        else:
            self.carrier_accum += self.carrier_phase
            self.carrier_phase = 0

    # These are used to change the code/carrier by the specified ammount
    def moveCodePhase(self,chips):
        self.code_phase += chips
        self.code_phase_offset += chips
        self.wrapCode()

    def moveCarrierPhase(self,cycles):
        self.carrier_phase += cycles
        self.carrier_phase_offset += cycles
        self.wrapCarrier()

    # Get and set routines that work in engineering units
    def setCodeFreqOffsetHz(self,freq):
        self.code_freq_offset = 0 * (freq * self.code_chiplen) * self.tick_size / self.code_chiplen

    def getCodeFreqOffsetHz(self):
        return  self.code_freq_offset / self.tick_size

    def getCodePhaseOffsetSec(self):
        return self.code_phase_offset * self.code_chiplen

    def setCarrierFreqOffsetHz(self,freq):
        self.carrier_freq_offset = freq * self.tick_size

    def getCarrierFreqOffsetHz(self):
        return self.carrier_freq_offset / self.tick_size

    def tick(self):
       self.local_time += self.tick_size
       code_phase_delta = self.chips_per_tick + self.code_freq_offset
       self.code_phase += code_phase_delta
       self.code_phase_offset += self.code_freq_offset
       self.wrapCode()
       
       carrier_update =self.cycles_per_tick + self.carrier_freq_offset
       self.carrier_phase += carrier_update
       self.carrier_phase_offset += self.carrier_freq_offset
       self.wrapCarrier()

    def reset(self):
        self.code_phase = 0
        self.code_phase_offset = 0
        self.code_freq_offset = 0
        self.carrier_phase = 0
        self.carrier_phase_offset = 0
        self.carrier_freq_offset = 0
        self.carrier_accum = 0
        self.local_time = 0
        self.code_generator.reset()

    def dump(self):
        print("# ", self.code_generator.sv," ",self.code_generator.code)
        print(":")
        print("# -- tick Size: ", self.tick_size * 1e6, " us")
        print(", code ChipLen: ", self.code_chiplen * 1e6, " us")
        print(", chips Per Tick:", self.chips_per_tick)
        print("# -- LO carrier Freq: ", self.carrier_freq * 1e-3, " kHz")
        print(", cycles Per Tick: ", self.cycles_per_tick)
        print("# -- local Time: ", self.local_time * 1e6, " us")
        print(", code phase: ", self.code_phase, " chips")
        print("# -- code phase Offset: ", self.code_phase_offset, " chips")
        print(", code Freq Offset: ", self.code_freq_offset, " chips/tick")
        print("# -- carrier Phase: ", self.carrier_phase)
        print(", carrier Freq Offset: ", self.carrier_freq_offset, " cycles/tick")
        
def main():    
    CCCodeGen = CACodeGenerator(3)
    CCRep = CCReplica(1/20e6,1.023e6,0.42e6,CCCodeGen)
    CCRep.reset()
    real=[]
    imag=[]
    for k in range(10000):
       carrier = CCRep.getCarrier();
       code = 1 if CCRep.getCode() else -1
       CCRep.tick()
       real.append(code*carrier[0])
       imag.append(code*carrier[1])

    x= range(10000)
    plt.plot(x,real)
    plt.ylim(-10,10)
    plt.show()

if __name__ == '__main__':
    main()