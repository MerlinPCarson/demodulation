import soundfile as sf
import numpy as np 
import matplotlib.pyplot as plt 
import sys
from math import pi, sin

WAV_DATATYPE = 'float32'
BAUD_RATE = 300
MARK = 1
SPACE = 0

class Decoder:

    def __init__(self, sampleRate, frameSize, spaceFrame, markFrame):
        self.sampleRate = sampleRate
        self.frameSize = frameSize
        self.spaceFreq = self.getFreq(spaceFrame)
        self.markFreq = self.getFreq(markFrame) 
        self.frame = []
    
    def getFreq(self, frame):
        spec = np.fft.fft(frame)
        freqs = np.fft.fftfreq(len(spec))
        idx = np.argmax(spec[:len(spec)//2])
        freq = freqs[idx] 
        freq_in_hertz = abs(freq * 48000)
        return freq_in_hertz

    def decode(self, frame):
        freq = self.getFreq(frame)
        if freq == self.markFreq:
            return MARK
        elif freq == self.spaceFreq:
            return SPACE
        assert True, "Unknown frequency detected"


def convertBits(bits):
    # bits are in little endian order
    bits = np.flip(bits)
    # dot bits with power of 2 array
    asciiVal = bits.dot(np.flip(2**np.arange(bits.size)))
    return chr(asciiVal) 

def decode(modFile):
    message = []

    # load wav data
    data, sampleRate = sf.read(modFile, dtype=WAV_DATATYPE)
    frameSize = sampleRate // BAUD_RATE
    
    # stats
    print(f"frame size: {frameSize}, sample rate: {sampleRate}, number of samples: {len(data)}")
    print(f"number of chars in message: {len(data)/1600}")
    print(f"data: {data}")

    # create decoder object
    decoder = Decoder(sampleRate, frameSize, data[:frameSize], data[frameSize:2*frameSize])

    sampleNum = 0
    start = False
    end = False
    cntBits = 0
    bits = []
    message = []

    while(sampleNum < len(data)):
        frame = data[sampleNum:sampleNum+frameSize]

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
            message.append(convertBits(bits))
            bits = []
            cntBits = 0
            start = False
        
        sampleNum += frameSize

    return message

def main():
    #modFile = sys.argv[1]
    modFile = 'test1.wav'
    modFile = 'test2.wav'
    modFile = 'carson.wav'

    # decodes message in modulation file
    message = decode(modFile)
    print(f"message is: {''.join(message)}")

    print("demodularization complete")


if __name__ == "__main__":
    main()