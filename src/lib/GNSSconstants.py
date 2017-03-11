#!/usr/bin/python3
# -*- coding: UTF-8 -*- 

class GNSSconstants(object):
    """docstring for GNSSconstants"""

    # GPS value of PI also specified by GAL
    PI        = 3.141592653589793238462643383280
    # GPS value of PI*2
    TWO_PI    = 6.283185307179586476925286766559
    # GPS value of PI**0.5
    SQRT_PI   = 1.772453850905516027298167483341
    # relativity constant (sec/sqrt(m))
    REL_CONST = -4.442807633e-10
    # m/s, speed of light this value defined by GPS but applies to GAL and GLO.
    C_MPS     = 2.99792458e8
    # Conversion Factor from degrees to radians (units: degrees^-1)
    DEG_TO_RAD= 1.7453292519943e-2
    # Conversion Factor from radians to degrees (units: degrees)
    RAD_TO_DEG= 57.295779513082

    # Hz, GPS Oscillator or chip frequency
    OSC_FREQ_GPS  = 10.23e6
    # Hz, GPS chip rate of the P & Y codes
    PY_CHIP_FREQ_GPS = OSC_FREQ_GPS
    # Hz, GPS chip rate of the C/A code
    CA_CHIP_FREQ_GPS = OSC_FREQ_GPS / 10.0
    # Hz, GPS Base freq w/o relativisitic effects
    RSVCLK_GPS    = 10.22999999543e6
    # GPS L1 carrier frequency in Hz
    L1_FREQ_GPS   = 1575.42e6
    # GPS L2 carrier frequency in Hz
    L2_FREQ_GPS   = 1227.60e6
    # GPS L5 carrier frequency in Hz.
    L5_FREQ_GPS   = 1176.45e6
    # GPS L1 carrier wavelength in meters
    L1_WAVELENGTH_GPS  = 0.190293672798
    # GPS L2 carrier wavelength in meters
    L2_WAVELENGTH_GPS  = 0.244210213425
    # GPS L5 carrier wavelength in meters.
    L5_WAVELENGTH_GPS  = 0.254828049
    # GPS L1 frequency in units of oscillator frequency
    L1_MULT_GPS   = 154.0
    # GPS L2 frequency in units of oscillator frequency
    L2_MULT_GPS   = 120.0
    # GPS L5 frequency in units of oscillator frequency.
    L5_MULT_GPS   = 115.0
    # GPS Gamma constant
    GAMMA_GPS = 1.646944444
    # Reference Semi-major axis. From IS-GPS-800 Table 3.5-2 in meters.
    A_REF_GPS = 26559710.0
    # Omega reference value from Table 30-I converted to radians
    OMEGADOT_REF_GPS = -2.6e-9 * PI

    # def getLegacyFitInterval(iodc, fiti):
    #     # check the IODC 
    #     if (iodc < 0 or iodc > 1023):
    #     # error in iodc, return minimum fit 
    #         return 4
    #     if ( ( ( (fiti == 0) and (iodc & 0xFF) < 240 ):
    #          or (iodc & 0xFF) > 255 ) ):
    #         # /* fit interval of 4 hours */
    #         return 4
    #     elif (fiti == 1):
    #         if( ((iodc & 0xFF) < 240 or (iodc & 0xFF) > 255)):
    #             # fit interval of 6 hours 
    #             return 6
    #         elif(iodc >=240 and iodc <=247):
    #             # fit interval of 8 hours */
    #             return 8
    #         elif( ( (iodc >= 248) and (iodc <= 255) ) or iodc == 496 ):         
    #             # fit interval of 14 hours 
    #             return 14
    #         elif((iodc >= 497 and iodc <=503) or (iodc >= 1021 and iodc <= 1023)):
         
    #             # fit interval of 26 hours
    #             return 26
    #         elif(iodc >= 504 and iodc <=510):
         
    #             # fit interval of 50 hours
    #             return 50
    #         elif( iodc == 511 or ( (iodc >= 752) and (iodc <= 756) ) ):
    #             # fit interval of 74 hours 
    #             return 74
    #         elif(iodc == 757):
    #             # fit interval of 98 hours
    #             return 98
    #         else:
    #             print("Invalid IODC Value For sv Block")
    #             return -1
    #     else
    #         # error in ephemeris/iodc, return minimum fit 
    #         return 4