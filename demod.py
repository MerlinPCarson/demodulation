import soundfile as sf
import numpy as np 
import matplotlib.pyplot as plt 
import sys
from math import pi, sin

WAV_DATATYPE = 'float32'
BAUD_RATE = 300
MARK = 1
SPACE = 0
MARK_FREQ = 2225 
SPACE_FREQ = 2025 

class Goertzel:
    
    def __init__(self, sampleRate, frameSize, frequency):
        self.w0 = 2*pi*frequency/sampleRate
        self.norm = np.exp(np.complex(0, self.w0 * frameSize))
        self.coeff = np.array([np.exp(np.complex(0, -self.w0 * k)) for k in range(frameSize)])

    def filter(self, samples):
        assert len(samples) == len(self.coeff), "Window size does not match number of coeffecients"
        return self.norm * np.dot(samples, self.coeff)
        
        
class Demodulator:

    def __init__(self, sampleRate, frameSize, spaceFrame, markFrame):
        self.sampleRate  = sampleRate
        self.frameSize   = frameSize
        self.filterSpace = Goertzel(sampleRate, frameSize, SPACE_FREQ) 
        self.filterMark  = Goertzel(sampleRate, frameSize, MARK_FREQ) 

    def decode(self, frame):
        markMag  = abs(self.filterMark.filter(frame))
        spaceMag = abs(self.filterSpace.filter(frame))
        if markMag > spaceMag:
            return MARK
        elif spaceMag > markMag:
            return SPACE
        
        assert True, "Abiguous detection"


def convertBits(bits):
    # bits are in little endian order
    bits = np.flip(bits, axis=0)
    # dot bits with power of 2 array
    asciiVal = bits.dot(np.flip(2**np.arange(bits.size), axis=0))
    return chr(asciiVal) 

def decode(modFile):
    message = []

    # load wav data
    data, sampleRate = sf.read(modFile, dtype=WAV_DATATYPE)
    frameSize = sampleRate // BAUD_RATE
    
    # stats
    print(f"Stats: sample rate {sampleRate}, frame size {frameSize}")

    # create decoder object
    decoder = Demodulator(sampleRate, frameSize, data[:frameSize], data[frameSize:2*frameSize])

    start = False
    cntBits = 0
    bits = []
    message = []

    print("\n\"", end=" ")

    # mimic real-time, read blocks from file like it's a buffer
    for frame in sf.blocks(modFile, blocksize = frameSize):

        # wait for start bit
        if start == False and decoder.decode(frame) == SPACE:
            start = True

        # read the byte 
        elif start == True and cntBits < 8:
            bits.append(decoder.decode(frame))
            cntBits += 1

        elif start == True and cntBits == 8:
            # verify next bit is end bit
            assert decoder.decode(frame) == MARK, "Stop bit not detected"
            letter = convertBits(bits)
            print(letter, end=" ")
            message.append(letter)
            bits = []
            cntBits = 0
            start = False
        
    print(" \"\n")

    return message

def main():
    modFile = sys.argv[1]

    # decodes message in modulation file
    message = decode(modFile)

    print("Demodularization complete!")


if __name__ == "__main__":
    main()
