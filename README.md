# demodulation
a demodulator for a limited subset of the Bell 103 modem protocol.

Usage:
  python3 demod.py <wave_file>
  
Requirements:
  soundfile
  numpy
  
This is an 8N1 protocol. The program reads in SAMPLERATE/BAUDRATE blocks from a wav, passed in as an argument. Each block is passed through a Goertzel filter at the answer frequencies of 2225 for a mark and 2025 for a space. The magnitude of the filter that is high determines a 1 bit for mark and a 0 bit for space. The program loops on a continuous mark signal until a space signal is read, signifying the start bit. The next eight bits are read in in little indian order. The bits are flipped and dotted with an eight element power of two array in reverse order. The ASCII character of that value is printed to the console. The program then verifies the next bit is a 1, signifying the stop bit. This loop is continued until the end the wave file. This program could be easily modified to read in blocks from an audio buffer instead of a wave file, so as to run with a real time transmission.
  
