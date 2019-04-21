import soundfile as sf
import numpy as np 
import matplotlib as plt 
import sys

WAV_DATATYPE = 'float32'
FRAME_SIZE = 160
MARK = 1
SPACE = 0

def goertzelSpace(sampleNum):
    return SPACE 

def goertzelMark(sampleNum):
    return MARK 

def waitForMark(data, sampleNum):
    
    while(goertzelSpace(sampleNum) != SPACE):
        sampleNum += FRAME_SIZE 

    return sampleNum + FRAME_SIZE  

def readByte(data, sampleNum):
    bits = []

    # read the 8 bits, little endian order
    for x in range(8):
        bits.append(goertzelMark(sampleNum+(FRAME_SIZE*x)))

    # verify 9th bit is a MARK
    assert goertzelMark(sampleNum+(8*FRAME_SIZE)) == MARK

    return bits, sampleNum + 9 * FRAME_SIZE

def convertBits(bits):
    return '?'

def decode(modFile):
    message = []

    # load wav data
    data, sampleRate = sf.read(modFile, dtype=WAV_DATATYPE)
    print(f"sample rate: {sampleRate}, number of samples: {len(data)}")
    print(f"number of chars in message: {len(data)/1600}")
    print(f"data: {data}")

    sampleNum = 0
    while(sampleNum < len(data)):
        sampleNum = waitForMark(data, sampleNum) 
        print(f"start bit competed at {sampleNum}")
        bits, sampleNum = readByte(data, sampleNum)
        print(f"message competed at {sampleNum}")
        message.append(convertBits(bits))

    return message


def main():
    #modFile = sys.argv[1]
    modFile = 'test1.wav'
    #modFile = 'test1.wav'

    # decodes message in modulation file
    message = decode(modFile)
    print(f"length of message is {len(message)}")
    print(f"message is {message}")

    print("demodularization complete")


if __name__ == "__main__":
    main()