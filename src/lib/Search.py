#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import CACodeGenerator
import CCReplica
import GNSSconstants
import InputIQ
import datetime

class Search(object):
    """docstring for Search"""

    def __init__(self, prn):
        super(Search, self).__init__()
        
        self.adc_amplitude = GNSSconstants.GNSSconstants.ADC_AMPLITUDE
        self.adc_sample_freq = GNSSconstants.GNSSconstants.L1_FREQ_ADC_SAMPLE
        self.chip_freq = GNSSconstants.GNSSconstants.CA_CHIP_FREQ_GPS
        self.inter_freq = GNSSconstants.GNSSconstants.L1_INTER_GPS
        self.sample_period = GNSSconstants.GNSSconstants.SAMPLE_PERIOD
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        # page 356, the maximum Doppler frequency offset is +-10kHz
        self.freqSearchWidth = 20000 
        self.freqBinWidth = 200 
        self.bins = (20000 // 200 + 1)
        # odd values recommended because of possible NAV change.
        self.periods = GNSSconstants.GNSSconstants.SAMPLE_PERIOD
        # the period of C/A code is 1ms
        self.numSamples = int(self.adc_sample_freq * self.periods)
        self.prn = prn
        self.peak = 0.00008

    def process(self):
        pyfftw.interfaces.cache.enable()

        # Get input code
        IQ_input = InputIQ.InputIQ("../gps_adc.txt")
        input_td = numpy.array(IQ_input.read(self.num_samples))

        # Convert input code to frequency domain.
        # Consider to share these results to all prns
        # input_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        input_fd = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        fft_input = pyfftw.FFTW(input_td, input_fd,direction="FFTW_FORWARD",flags=('FFTW_ESTIMATE',),threads=2)
        fft_input_result = fft_input()
        input_fd_conj = numpy.conj(input_fd)

        # Init the peak and peak of bin
        peak = 0.0
        dop_freq = self.inter_freq
        peak_shift = 0

        # Create local code replicas for each frequency bin.
        # Consider to output these FFT results to file.
        PrnCACodeGen = CACodeGenerator.CACodeGenerator(self.prn)
        PrnCC_td = pyfftw.empty_aligned(self.numSamples, dtype='complex128')
        PrnCC_fd  = pyfftw.empty_aligned(self.numSamples, dtype='complex128')
        f = -self.freqSearchWidth / 2
        multi_plot=[]
        for i in range(self.bins):
            PrnCCGen = CCReplica.CCReplica(self.adc_sample_freq,self.chip_freq,
                          self.inter_freq+f,PrnCACodeGen)
            PrnCCGen.reset(0)
            for j in range(self.numSamples):
                carrier = PrnCCGen.getCarrier()
                code = PrnCCGen.getCodePrompt()
                PrnCC_td[j] = carrier * code
                PrnCCGen.tick()

            # Convert local code replicas to frequency domain.
            fft_PrnCC = pyfftw.FFTW(PrnCC_td, PrnCC_fd,direction="FFTW_FORWARD",flags=('FFTW_ESTIMATE',),threads=1)
            fft_PrnCC_result = fft_PrnCC()
            # Multiply conjugate of input frequency samples by local frequency samples (point by point).
            multi_fd=(PrnCC_fd*input_fd_conj)/self.numSamples
            
            # Convert back to time domain and find peak.
            multi_td = pyfftw.empty_aligned(self.numSamples, dtype='complex128')
            fft_multi = pyfftw.FFTW(multi_fd, multi_td,direction="FFTW_BACKWARD",flags=('FFTW_ESTIMATE',),threads=1)
            fft_multi_result = fft_multi()
            multi_td_abs = abs(multi_td)/math.sqrt(self.num_samples)
            multi_td_max = multi_td_abs.max()
            if multi_td_max > peak:
                peak = multi_td_max
                dop_freq = self.inter_freq+f
                peak_shift = multi_td_abs.argmax()
                multi_plot = multi_td_abs
            print(f,peak)
            f += self.freqBinWidth

        plt.plot(multi_plot)
        plt.show()

        peak_shift = peak_shift % (self.adc_sample_freq*1e-3)
        # print(peak,dop_freq,peak_shift)
        if peak <= self.peak:
            print("Prn:%d Unable to acquire."%self.prn)
            return False, 0, 0, 0
        else:
            print("Prn:%d - Peak:%f - Doppler:%f - Shift:%d\n"%(self.prn,peak,dop_freq,peak_shift))
            # Subtracting 5 right now to make sure the tracker starts on the "left side" of the peak.
            return True, peak, dop_freq, peak_shift

def main():
    acquire = Search(3)
    acquire, peak, dop_freq, peak_shift = acquire.process()
    if(acquire):
        print(peak,dop_freq,peak_shift)

if __name__ == '__main__':
    main()
