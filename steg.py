"""PyAudio Example: Play a wave file."""

import pyaudio
import wave
import sys
import numpy as np
import struct

CHUNK = 1024

if len(sys.argv) < 2:
    print("Plays a wave file.\n\nUsage: %s filename.wav" % sys.argv[0])
    sys.exit(-1)

wf = wave.open(sys.argv[1], 'rb')
swidth = 2
# instantiate PyAudio (1)
p = pyaudio.PyAudio()

# open stream (2)
stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                input=True)
data = wf.readframes(CHUNK)
num = 0
# play stream (3)
while 200 > num:
    stream.write(data)

    data = wf.readframes(CHUNK)
    num += 1

data = stream.read(CHUNK)
data = np.fromstring(data, dtype=np.int16)
data *= 2

# stop stream (4)
stream.stop_stream()
stream.close()


def stretch(snd_array, factor, window_size, h):
    """ Stretches/shortens a sound, by some factor. """
    phase = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = np.zeros(int(len(snd_array) / factor + window_size))
    for i in np.arange(0, len(snd_array) - (window_size + h), h*factor):
        i = int(i)
        # Two potentially overlapping subarrays
        a1 = snd_array[i: i + window_size]
        a2 = snd_array[i + h: i + window_size + h]

        # The spectra of these arrays
        s1 = np.fft.fft(hanning_window * a1)
        s2 = np.fft.fft(hanning_window * a2)

        # Rephase all frequencies
        phase = (phase + np.angle(s2/s1)) % 2*np.pi

        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))
        i2 = int(i/factor)
        result[i2: i2 + window_size] += hanning_window*a2_rephased.real
    return result.astype('int16')

def speedx(sound_array, factor):
    """ Multiplies the sound's speed by some `factor` """
    indices = np.round( np.arange(0, len(sound_array), factor) )
    indices = indices[indices < len(sound_array)].astype(int)
    return sound_array[ indices.astype(int) ]

def pitchshift(snd_array, n, window_size=2**13, h=2**11):
    """ Changes the pitch of a sound by ``n`` semitones. """
    factor = 2**(1.0 * n / 12.0)
    stretched = stretch(snd_array, 1.0/factor, window_size, h)
    return speedx(stretched[window_size:], factor)

def playAudio(audio, samplingRate, channels):
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=samplingRate,
                    output=True)
    sound = (audio.astype(np.int16).tostring())
    stream.write(sound)

    stream.stop_stream()
    stream.close()
    p.terminate()
    return

# close PyAudio (5)
p.terminate()
CHANNELS = 2
RATE = 44100
playAudio(data, RATE, CHANNELS)