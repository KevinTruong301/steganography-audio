import wave
import numpy as np
import pyaudio
import binascii
import sys

def text2bin(text):
    binary = ''.join(format(ord(x), 'b').zfill(8) for x in text)
    return binary

#turn binary to ASCII text
def bin2text(bin):
    a = int(bin, 2)
    hex_string = '%x' % a
    n = len(hex_string)
    z = binascii.unhexlify(hex_string.zfill(n + (n & 1)))
    text=z.decode('ascii')
    return text

def encode(audioFile):
    wr = wave.open(audioFile, 'r')
    # Set the parameters for the output file.
    print(audioFile)
    par = list(wr.getparams())
    par[3] = 0  # The number of samples will be set by writeframes.
    par = tuple(par)
    ww = wave.open(str(audioFile)[:-4] + "_encoded.wav" , 'w')
    ww.setparams(par)

    fr = 20
    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
    # A larger number for fr means less reverb.
    c = int(wr.getnframes()/sz)  # count of the whole file
    print(c)
    shift = 0//fr  # shifting 100 Hz

    message = sys.argv[3]
    print(message)
    binMessage = text2bin(message)

    binLength = text2bin(str(len(binMessage)))

    count = 0
    print(len(binMessage))
    #encode length

    if(c < len(binMessage) + 32):
        print("Audio file not large enough for message")
        exit()

    for i in range(32 - len(binLength)):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        print(da)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + '0'
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())

    for i in binLength:
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + i
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())

    for i in binMessage:
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + i
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())
    
    for i in range(c - 32 - len(binMessage)):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        ww.writeframes(da.tostring())

    wr.close()
    ww.close()

def decode(audioFile):
    wr = wave.open(audioFile, 'r')

    fr = 20
    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
    # A larger number for fr means less reverb.
    c = int(wr.getnframes()/sz)  # count of the whole file
    shift = 0//fr  # shifting 100 Hz

    length = ""

    for i in range(32):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        length += b[-1:]

    length = int(bin2text(length))

    message = ""
    for i in range(length):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        message += b[-1:]

    message = bin2text(message)
    print (message)
    wr.close()


if(sys.argv[1] == '-e'):
    encode(sys.argv[2])

if(sys.argv[1] == '-d'):
    decode(sys.argv[2])

# CHUNK = 1024

# wf = wave.open('test.wav', 'rb')

# # instantiate PyAudio (1)
# p = pyaudio.PyAudio()

# # open stream (2)
# stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                 channels=wf.getnchannels(),
#                 rate=wf.getframerate(),
#                 output=True)

# # read data
# data = wf.readframes(CHUNK)

# # play stream (3)
# while len(data) > 0:
#     stream.write(data)
#     data = wf.readframes(CHUNK)

# # stop stream (4)
# stream.stop_stream()
# stream.close()

# # close PyAudio (5)
# p.terminate()