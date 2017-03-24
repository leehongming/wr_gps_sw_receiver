#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

from CACodeGenerator import *
from GNSSconstants import *
import ComplexMath
import matplotlib.pyplot as plt
import pyfftw
import numpy

class CCReplica(object):
    """This is a intended to generate a local replica of a single code/carrier"""    
    def __init__(self, nco_freq, code_freq, carrier_freq, code_generator):
        super(CCReplica, self).__init__()
        self.nco_freq = nco_freq
        self.tick_len = 1.0 / nco_freq
        self.code_chiplen = 1.0 / code_freq
        self.carrier_freq = carrier_freq
        self.chips_per_tick = code_freq / nco_freq
        self.cycles_per_tick = carrier_freq / nco_freq 
        self.code_prompt = -1.0
        self.code_early = -1.0
        self.code_late = -1.0
        self.code_prev = -1.0
        self.code_curr = -1.0
        self.code_next = -1.0
        self.code_latch = -1.0
        self.code_phase = 0
        self.code_phase_late = 0
        self.code_phase_offset = 0
        self.code_freq_offset = 0
        self.carrier_phase = 0
        self.carrier_phase_offset = 0
        self.carrier_freq_offset = 0
        self.carrier_accum = 0
        self.local_time = 0
        self.code_generator = code_generator

    def getCodePrompt(self):
        return self.code_prompt
    
    def getCodeEarly(self):
        return self.code_early
    
    def getCodeLate(self):
        return self.code_late

    def getCarrier(self): # value between -1 and 1
        return ComplexMath.sincos(2.0 * GNSSconstants.PI * self.carrier_phase)

    def updateCode(self):
        if (self.code_phase_late<1):
            self.code_early = self.code_next
            self.code_late = self.code_curr
        # update code_late and code_early
        elif (self.code_phase_late<2):
            self.code_phase_late -= 1
            self.code_curr = 1.0 if (self.code_generator.getCode()) else -1.0
            self.code_late = self.code_prev * (1.0 - self.code_phase_late) + self.code_curr * self.code_phase_late
            self.code_prev = self.code_curr
            self.code_generator.popup()
            self.code_next = 1.0 if (self.code_generator.getCode()) else -1.0
            self.code_early = self.code_curr * (1.0 - self.code_phase_late) + self.code_next * self.code_phase_late
        else:
            self.code_generator.setIndex(self.code_generator.getIndex() + int(self.code_phase_late))
            self.code_phase_late -= int(self.code_phase_late)
            self.code_prev = 1.0 if self.code_generator.getCode() else -1.0
            self.code_curr = 1.0 if self.code_generator.getCode() else -1.0
            self.code_generator.popup()
            self.code_next = 1.0 if self.code_generator.getCode() else -1.0
            self.code_late = self.code_curr
            self.code_early = self.code_next

        if self.code_phase < 1:
            self.code_prompt = self.code_latch
        elif (self.code_phase<2):
            self.code_phase -= 1
            self.code_latch = self.code_next
            self.code_prompt = self.code_curr * (1.0 - self.code_phase) + self.code_next * self.code_phase
        else:
            self.code_phase -= int(self.code_phase)
            if self.code_phase_late<0.5:
                self.code_latch = self.code_curr
            else:
                self.code_latch = self.code_next

            self.code_prompt = self.code_latch

    def updateCarrier(self):
        if (self.carrier_phase<1):
            return
        elif (self.carrier_phase<2):
            self.carrier_phase -=1
            self.carrier_accum +=1
        else:
            self.carrier_phase -= int(self.carrier_phase)
            self.carrier_accum += int(self.carrier_phase)

    # These are used to change the code/carrier by the specified ammount
    def moveCodePhase(self,chips):
        self.code_phase += chips
        self.code_phase_late += chips
        self.code_phase_offset += chips
        self.updateCode()

    def moveCarrierPhase(self,cycles):
        self.carrier_phase += cycles
        self.carrier_phase_offset += cycles
        self.updateCarrier()

    def setCarrierFreqOffsetHz(self,freq):
        self.carrier_phase_offset = freq / self.nco_freq

    def getCarrierFreqOffsetHz(self):
       return self.carrier_phase_offset * self.nco_freq

    def tick(self):
       self.local_time += self.tick_len
       self.code_phase += (self.chips_per_tick + self.code_freq_offset)
       self.code_phase_late += (self.chips_per_tick + self.code_freq_offset)
       self.code_phase_offset += self.code_freq_offset
       self.updateCode()
       self.carrier_phase += (self.cycles_per_tick + self.carrier_freq_offset)
       self.carrier_phase_offset += self.carrier_freq_offset
       self.updateCarrier()

    def reset(self,shift):
        self.code_generator.reset()
        self.code_prev = 1.0 if self.code_generator.getCode() else -1.0        
        self.code_late = 1.0 if self.code_generator.getCode() else -1.0
        self.code_prompt = 1.0 if self.code_generator.getCode() else -1.0
        self.code_latch = 1.0 if self.code_generator.getCode() else -1.0
        self.code_curr = 1.0 if self.code_generator.getCode() else -1.0        
        self.code_generator.popup()
        self.code_next = 1.0 if self.code_generator.getCode() else -1.0
        self.code_early = 1.0 if self.code_generator.getCode() else -1.0
        self.code_phase = 0.5
        self.code_phase_late = 0
        self.code_phase_offset = 0
        self.carrier_phase = 0
        self.carrier_phase_offset = 0
        self.carrier_accum = 0
        self.local_time = 0

    def dump(self):
        print("# ", self.code_generator.sv," ",self.code_generator.code)
        print(":")
        print("# -- NCO Freq: ", self.nco_freq, " Hz")
        print(", code ChipLen: ", self.code_chiplen * 1e6, " us")
        print(", chips Per Tick:", self.chips_per_tick)
        print("# -- LO carrier Freq: ", self.carrier_freq * 1e-3, " kHz")
        print(", cycles Per Tick: ", self.cycles_per_tick)
        print("# -- local Time: ", self.local_time * 1e6, " us")
        print(", code phase: ", self.code_phase, " chips")
        print("# -- code phase Offset: ", self.code_phase_offset, " chips")
        print("# -- carrier Phase: ", self.carrier_phase)
        
def main():    
    CCCodeGen = CACodeGenerator(3)
    CCCodeGen1 = CACodeGenerator(3)
    CCRep = CCReplica(15.625e6,1.023e6,4.1309375e6,CCCodeGen)

    # CCCodeGen2 = CACodeGenerator(3)
    # CCRep2 = CCReplica(15.625e6,1.023e6,4.1309375e6,CCCodeGen2)
    # CCRep2.reset(0)
    pyfftw.interfaces.cache.enable()
    a=[]
    b=[]
    c=[]

    CCRep.reset(0)
    for k in range(1000):
        a.append(CCRep.getCodeLate())
        c.append(CCRep.getCodePrompt())
        CCRep.tick()

    CCRep.reset(0)
    CCRep.moveCodePhase(1)
    for k in range(100):
        b.append(CCRep.getCodeLate())
        CCRep.tick()

    aa=numpy.array(a)
    bb=numpy.array(b)
    cc=numpy.array(c)
    plt.ylim(-2,2)
    plt.plot(aa)
    plt.plot(cc)
    plt.show()

if __name__ == '__main__':
    main()
