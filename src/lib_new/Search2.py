#!/usr/bin/python3
# -*- coding: UTF-8 -*- 
import pyfftw
import math
import numpy
import matplotlib.pyplot as plt
import datetime
import lib_new.CACodeGen as CACodeGen
import lib_new.NCO as NCO
import lib_new.InputIQ as InputIQ

class Search(object):
    """docstring for Search"""
    def __init__(self, prn, InputIQ):
        super(Search, self).__init__()
        
        self.adc_sample_freq = 15.625e6 
        self.ca_code_freq = 1.023e6
        self.inter_freq = 4.1309375e6
        # odd values recommended because of possible NAV change.
        self.sample_period = 1e-3 # 1ms
        # the period of C/A code is 1ms
        self.num_samples = int(self.adc_sample_freq * self.sample_period)
        # page 356, the maximum Doppler frequency offset is +-10kHz
        self.freqSearchWidth = 20000
        self.freqBinWidth = 200
        self.bins = (20000 // 200 + 1)    
        self.prn = prn
        self.IQ_input = InputIQ
        self.search_snr = 8


    def process(self):
        pyfftw.interfaces.cache.enable()
        # Get input code
        input_td = numpy.array(self.IQ_input.read(self.num_samples))

        # Convert input code to frequency domain.
        # Consider to share these results to all prns
        # input_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        input_fd = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        fft_input = pyfftw.FFTW(input_td, input_fd,direction="FFTW_FORWARD",flags=('FFTW_ESTIMATE',),threads=2)
        fft_input_result = fft_input()
        input_fd_conj = numpy.conj(input_fd)

        # Init the peak and peak of bin
        snr_max = 0.0
        dop_freq = self.inter_freq
        peak_shift = 0

        code_td  = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        code_fd = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        local_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        local_fd = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        multi_td = pyfftw.empty_aligned(self.num_samples, dtype='complex128')
        multi_fd = pyfftw.empty_aligned(self.num_samples, dtype='complex128')

        # Create local code replicas for each frequency bin.
        code_gen = CACodeGen.CACodeGen(self.prn)
        code_nco_len = 8
        code_nco = NCO.NCO(code_nco_len,0,self.adc_sample_freq,self.ca_code_freq)
        code_index = 0
        update = False
        for i in range(self.num_samples):
            code = 1 if code_gen.getCode(code_index) else -1
            if (update):
                code_td[i] = complex(code*code_phase+code_prev*(1-code_phase))
            else:
                code_td[i] = complex(code,0)
            update, code_phase = code_nco.tick()
            if (update):
                code_prev = code
                code_index+=1
            else:
                code_prev = 0

        f = -self.freqSearchWidth / 2
        multi_plot=[]
        for i in range(self.bins):
            # Create local carrier for each frequency bin.
            # Consider to output these FFT results to file.
            carrier_nco_len = 4
            carrier_nco = NCO.NCO(carrier_nco_len,0,self.adc_sample_freq,self.inter_freq+f)
            for i in range(self.num_samples):
                carrier_sin, carrier_cos = carrier_nco.getSinCos()
                carrier = complex(carrier_cos,carrier_sin)
                local_td[i] = carrier * code_td[i]
                carrier_nco.tick()

            # Convert to frequency domain.
            fft_local = pyfftw.FFTW(local_td, local_fd,direction="FFTW_FORWARD",flags=('FFTW_ESTIMATE',),threads=1)
            fft_local_result = fft_local()
            # Multiply conjugate of input frequency samples by local code replicas samples (point by point).
            multi_fd=(local_fd*input_fd_conj)/self.num_samples
            
            # Convert back to time domain and find peak.
            fft_multi = pyfftw.FFTW(multi_fd, multi_td,direction="FFTW_BACKWARD",flags=('FFTW_ESTIMATE',),threads=1)
            fft_multi_result = fft_multi()
            multi_td_abs = abs(multi_td)/math.sqrt(self.num_samples)
            multi_td_max = multi_td_abs.max()
            multi_td_mean = multi_td_abs.mean()
            snr = multi_td_max / multi_td_mean
            if snr > snr_max:
                snr_max = snr
                dop_freq = self.inter_freq + f
                peak_shift = multi_td_abs.argmax()
                multi_plot = multi_td_abs
            print(f,snr)
            f += self.freqBinWidth

        peak_shift = peak_shift % (self.adc_sample_freq*1e-3)
        if snr_max <= self.search_snr:
            print("Prn:%d Unable to acquire."%self.prn)
            return False, 0, 0, 0
        else:
            print("Prn:%d - SNR:%f - Doppler:%f - Shift:%d\n"%(self.prn,snr_max,dop_freq,peak_shift))
            # Subtracting 5 right now to make sure the tracker starts on the "left side" of the peak.
            return True, snr_max, dop_freq, peak_shift

def main():
    IQ_input = InputIQ.InputIQ("../gps_adc.txt")
    acquire = Search(3,IQ_input)
    acquire.process()

if __name__ == '__main__':
    main()
