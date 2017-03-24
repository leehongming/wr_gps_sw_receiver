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
    # GPS L1 carrier wavelength in meters
    L1_WAVELENGTH_GPS  = 0.190293672798
    # GPS L1 intermediate frequency 
    # The configure value is 1575.42e6-15.625/16*1609e6
    L1_INTER_GPS   = 4.1309375e6
    # GPS ADC sample frequency in Hz
    L1_FREQ_ADC_SAMPLE = 15.625e6
    # sample period in second, odd values recommended because of possible NAV change.
    SAMPLE_PERIOD = 1e-3
    # ADC amplitude in 1/100 voltage
    ADC_AMPLITUDE = 90
    # GPS Gamma constant
    GAMMA_GPS = 1.646944444
    # Reference Semi-major axis. From IS-GPS-800 Table 3.5-2 in meters.
    A_REF_GPS = 26559710.0
    # Omega reference value from Table 30-I converted to radians
    OMEGADOT_REF_GPS = -2.6e-9 * PI
