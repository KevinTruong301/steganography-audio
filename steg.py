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
    par = list(wr.getparams())
    par[3] = 0  # The number of samples will be set by writeframes.
    par = tuple(par)
    ww = wave.open(str(audioFile)[:-4] + "_encoded.wav" , 'w')
    ww.setparams(par)

    fr = 20
    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
    # A larger number for fr means less reverb.
    c = int(wr.getnframes()/sz)  # count of the whole file

    message = sys.argv[3]
    binMessage = text2bin(message)

    binLength = text2bin(str(len(binMessage)))

    count = 0

    #Check if audio file is long enough to encode message
    if(c < len(binMessage) + 32):
        print("Audio file not large enough for message")
        exit()

    #Encoding 0's to fill in the rest of the 32 bits that are for length
    for i in range(32 - len(binLength)):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + '0'
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())

    #Encoding the length
    for i in binLength:
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + i
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())

    #Encoding the message
    for i in binMessage:
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        b = b[:len(b) -1] + i
        B = bin2text(b)
        da[0] = int(B)
        ww.writeframes(da.tostring())
    #Finishing the rest of the audio file
    for i in range(c - 32 - len(binMessage)):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        ww.writeframes(da.tostring())

    wr.close()
    ww.close()

def decode(audioFile):
    wr = wave.open(audioFile, 'r')

    fr = 20
    sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
    c = int(wr.getnframes()/sz)  # count of the whole file

    length = ""

    #Get the length of the message
    for i in range(32):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        length += b[-1:]

    length = int(bin2text(length))

    #Decode the message
    message = ""
    for i in range(length):
        da = np.fromstring(wr.readframes(sz), dtype=np.int32)
        b = text2bin(str(da[0]))
        message += b[-1:]

    #Change message from binary to text
    message = bin2text(message)
    
    print message
    wr.close()


if(sys.argv[1] == '-e'):
    encode(sys.argv[2])
elif(sys.argv[1] == '-d'):
    decode(sys.argv[2])
else:
    print "Invalid syntax" 
    print "Encode: python steg.py -e <audio file> <message>"
    print "Decode: python steg.py -d <audio file>" 
