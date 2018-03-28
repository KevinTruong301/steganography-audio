import wave
import numpy as np
import pyaudio
import binascii

wr = wave.open('audio.wav', 'r')
# Set the parameters for the output file.
par = list(wr.getparams())
par[3] = 0  # The number of samples will be set by writeframes.
par = tuple(par)
ww = wave.open('pitch1.wav', 'w')
ww.setparams(par)

fr = 20
sz = wr.getframerate()//fr  # Read and process 1/fr second at a time.
# A larger number for fr means less reverb.
c = int(wr.getnframes()/sz)  # count of the whole file
shift = 0//fr  # shifting 100 Hz



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

for num in range(c):

    da = np.fromstring(wr.readframes(sz), dtype=np.int32)
   
    b = text2bin(str(da[0]))
    b = b[:len(b) -1] + '1'
    B = bin2text(b)
    da[0] = int(B)

    ww.writeframes(da.tostring())



wr.close()
ww.close()

CHUNK = 1024

wf = wave.open('pitch1.wav', 'rb')

# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

# read data
data = wf.readframes(CHUNK)

# play stream (3)
while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()