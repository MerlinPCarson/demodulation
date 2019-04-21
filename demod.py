import soundfile as sf
import numpy as np 
import matplotlib as plt 
import sys

WAV_DATATYPE = 'float32'

def main():
    #modFile = sys.argv[1]
    modFile = 'test1.wav'
    #modFile = 'test1.wav'

    data, sampleRate = sf.read(modFile, dtype=WAV_DATATYPE)
    print(f"sample rate: {sampleRate}, number of samples: {len(data)}")
    print(f"number of chars in message: {len(data)/1600}")
    print(f"data: {data}")

    print("demodularization complete")


if __name__ == "__main__":
    main()