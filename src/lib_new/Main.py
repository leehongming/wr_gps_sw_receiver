# -*- coding: UTF-8 -*- 
#!/usr/bin/python3
import InputIQ
import Search
import Tracker
import BitSync
import FrameSync

class Main(object):
    """docstring for Main"""
    def __init__(self, IQ_input, prn=3):
        super(Main, self).__init__()
        self.prn = prn
        self.IQ_input = IQ_input
    
    def process(self):
        search_process = Search.Search(self.prn,self.IQ_input)
        find, snr_max, dop_freq, peak_shift = search_process.process()
        if (not find):
            print("Try another prn!\n")
        else:
            self.IQ_input.reset(int(peak_shift)-5)
            tracker_process = Tracker.Tracker(self.prn,dop_freq,self.IQ_input)
            bit_sync = BitSync.BitSync()
            frame_sync = FrameSync.FrameSync()
            fp = open("gps_nav_msg.txt","a+")
            frame_start = 0
            frame_word = 0
            frame_bit = 0
            frame_sign = 0
            while True:
                bit = tracker_process.process()
                sync_bit = bit_sync.process(bit)
                if (sync_bit):
                    print(sync_bit,)
                    if frame_start == 1:
                        if frame_sign>0:
                            if sync_bit == 1:
                                fp.write("1")
                            else:
                                fp.write("0")
                        else:
                            if sync_bit == 1:
                                fp.write("0")
                            else:
                                fp.write("1")

                        if frame_bit == 29:
                            frame_bit = 0
                            frame_word += 1
                            fp.write("\n"+str(frame_word)+":")
                            fp.flush()
                        else:
                            frame_bit += 1
                    else:
                        frame_sign = frame_sync.process(sync_bit)
                        if abs(frame_sign) == 8:
                            print("frame sync!")
                            fp.write("\nTLW:10001011")
                            frame_start = 1
                            frame_bit += 8

def main():
    IQ_input = InputIQ.InputIQ("../gps_adc.txt")
    for i in range(20,26):
        start = Main(IQ_input,i)
        start.process()

if __name__ == '__main__':
    main()
