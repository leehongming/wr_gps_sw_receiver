import pyfftw
import numpy
import matplotlib.pyplot as plt
import datetime

pyfftw.interfaces.cache.enable()
a = pyfftw.zeros_aligned(1048576, dtype='complex128')
b = pyfftw.zeros_aligned(1048576, dtype='complex128')
fft_object = pyfftw.FFTW(a, b,direction="FFTW_FORWARD",flags=('FFTW_ESTIMATE',),threads=2)
# ar, ai = numpy.random.randn(2, 1048576)
# a[:] = ar + 1j*ai

start = datetime.datetime.now()
fft_a = fft_object()
end = datetime.datetime.now()
print(end-start)

start = datetime.datetime.now()
fft_c = numpy.fft.fft(a)
end = datetime.datetime.now()
print(end-start)

plt.subplot(2,1,1)
plt.plot(fft_a)
plt.subplot(2,1,2)
plt.plot(fft_c)
plt.show()
