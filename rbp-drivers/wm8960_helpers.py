from __future__ import print_function

import sys
import wave
import getopt
import alsaaudio



CHANNELS = 2
RATE = 44100
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
PERIOD_SIZE = 160

FORMAT_DICT = {alsaaudio.PCM_FORMAT_S16_LE: 2}

def get_input_device(device="default"):
    # Open the device in nonblocking capture mode. The last argument could
    # just as well have been zero for blocking mode. Then we could have
    # left out the sleep call in the bottom of the loop
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,
                        alsaaudio.PCM_NONBLOCK,
                        channels=CHANNELS,
                        rate=RATE,
                        format=FORMAT,
                        periodsize=PERIOD_SIZE,
                        device=device)
    # The period size controls the internal number of frames per period.
    # The significance of this parameter is documented in the ALSA api.
    # For our purposes, it is suficcient to know that reads from the device
    # will return this many frames. Each frame being 2 bytes long.
    # This means that the reads below will return either 320 bytes of data
    # or 0 bytes of data. The latter is possible because we are in nonblocking
    # mode.
    inp.setperiodsize(PERIOD_SIZE)
    return inp

def get_saved_audio_file(output_file_path):
    output_file_path = str(output_file_path)
    f = wave.open(output_file_path, "wb")
    f.setnchannels(CHANNELS)
    f.setsampwidth(FORMAT_DICT[FORMAT])
    f.setframerate(44100)

    print(f'Input Device: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    return f

def record_audio_by_time(output_file_path, device="default", time=10000):
    # rough time in ms

    inp = get_input_device(device)
    f = get_saved_audio_file(output_file_path)

    saved_time = 0
    while True:
        l, data = inp.read()
        if l:
            f.writeframes(data)
            time.sleep(.001)
            # saves exactly time ms
            saved_time += 1
            if saved_time >= time:
                break
    f.close()

    return output_file_path

def open_audio_file(path):
    path = str(path)
    f = wave.open(path, "rb")
    print(f'Output File: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')

    return f

def play_audio(path, device="default"):
    f = open_audio_file(path)

    # 8bit is unsigned in wav files
    if f.getsampwidth() == 1:
        format = alsaaudio.PCM_FORMAT_U8
    # Otherwise we assume signed data, little endian
    elif f.getsampwidth() == 2:
        format = alsaaudio.PCM_FORMAT_S16_LE
    elif f.getsampwidth() == 3:
        format = alsaaudio.PCM_FORMAT_S24_LE
    elif f.getsampwidth() == 4:
        format = alsaaudio.PCM_FORMAT_S32_LE
    else:
        raise ValueError('Unsupported format')

    periodsize = f.getframerate() // 8

    out = alsaaudio.PCM(channels=f.getnchannels(),
                           rate=f.getframerate(),
                           format=format,
                           periodsize=periodsize,
                           device=device)
    data = f.readframes(periodsize)
    while data:
        # Read data from stdin
        out.write(data)
        data = f.readframes(periodsize)

    f.close()

if __name__ == "__main__":
    record_audio_by_time("out.wav")
    play_audio("out.wav")
