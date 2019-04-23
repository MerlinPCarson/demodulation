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
        self.spaceFreq   = self.getFreq(spaceFrame)
        self.markFreq    = self.getFreq(markFrame) 
        self.filterSpace = Goertzel(sampleRate, frameSize, SPACE_FREQ) 
        self.filterMark  = Goertzel(sampleRate, frameSize, MARK_FREQ) 

    def getFreq(self, frame):
        spec = np.fft.fft(frame)
        freqs = np.fft.fftfreq(len(spec))
        idx = np.argmax(spec[:len(spec)//2])
        freq = freqs[idx] 
        freq_in_hertz = abs(freq * 48000)
        return freq_in_hertz

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
    print(f"Stats: frame size {frameSize}, sample rate {sampleRate}, number of samples {len(data)}")
    #print(f"number of chars in message: {len(data)/1600}")
    #print(f"data: {data}")

    # create decoder object
    decoder = Demodulator(sampleRate, frameSize, data[:frameSize], data[frameSize:2*frameSize])

    sampleNum = 0
    start = False
    end = False
    cntBits = 0
    bits = []
    message = []

    #print(f"Space Filter(2225) Mag: {np.real(filterSpace.filter(data[:frameSize]))}")
    #print(f"Space Filter(2025) Mag: {np.real(filterMark.filter(data[:frameSize]))}")
    #print(f"Mark Frame(2225) Mag: {np.real(filterMark.filter(data[9*frameSize:10*frameSize]))}")
    #print(f"Mark Frame(2025) Mag: {np.real(filterSpace.filter(data[9*frameSize:10*frameSize]))}")

    print("\n\"", end=" ")
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
            letter = convertBits(bits)
            print(letter, end=" ")
            message.append(letter)
            bits = []
            cntBits = 0
            start = False
        
        sampleNum += frameSize
    print(" \"\n")

    return message

def main():
    modFile = sys.argv[1]
    #modFile = 'test1.wav'
    #modFile = 'test2.wav'
    #modFile = 'carson.wav'

    # decodes message in modulation file
    message = decode(modFile)
    #print(f"\nmessage is: {''.join(message)}\n")

    print("Demodularization complete!")


if __name__ == "__main__":
    main()
