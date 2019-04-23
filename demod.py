import soundfile as sf
import numpy as np 
import sys
from math import pi


# CONSTANTS
WAV_DATATYPE = 'float32'
BAUD_RATE = 300
MARK = 1
SPACE = 0
MARK_FREQ = 2225 
SPACE_FREQ = 2025 


# Goertzel filter
class Goertzel:
    
    def __init__(self, sampleRate, frameSize, frequency):
        self.w0 = 2*pi*frequency/sampleRate
        self.norm = np.exp(np.complex(0, self.w0 * frameSize))
        self.coeff = np.array([np.exp(np.complex(0, -self.w0 * k)) for k in range(frameSize)])

    def filter(self, samples):
        assert len(samples) == len(self.coeff), "Window size does not match number of coeffecients"
        return self.norm * np.dot(samples, self.coeff)
        
       
# Demodulator for answer signal from Bell 103 modem 
class Demodulator:

    def __init__(self, sampleRate, frameSize):
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
        
        assert True, "Ambiguous detection"


# flip the bits array and return ascii value as a char
def convertBits(bits):
    # bits are in little endian order
    bits = np.flip(bits, axis=0)
    # dot bits with power of 2 array
    asciiVal = bits.dot(np.flip(2**np.arange(bits.size), axis=0))
    return chr(asciiVal) 


# loads modulation file, reads and decodes ASCII message 1 frame at a time
def decode(modFile):
    # save message for return val
    message = []

    # load wav data and stats
    data, sampleRate = sf.read(modFile, dtype=WAV_DATATYPE)
    frameSize = sampleRate // BAUD_RATE
    print(f"\nStats: sample rate {sampleRate}, frame size {frameSize}")

    # create decoder object
    decoder = Demodulator(sampleRate, frameSize)

    # init loop vars
    start = False
    cntBits = 0
    bits = []

    # start of message
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
       
    # end of message 
    print(" \"\n")

    return message


def main():
    modFile = sys.argv[1]

    # decodes message in modulation file
    message = decode(modFile)

    print("Demodularization complete!\n")


if __name__ == "__main__":
    main()
