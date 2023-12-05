from __future__ import print_function

import time
import wave
import alsaaudio


CHANNELS = 1
RATE = 16000
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
    f.setframerate(RATE)

    print(f'Input Device: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    return f

# def record_audio_by_time(output_file_path, device="default", record_time=10):
#     # rough time in s
#     inp = get_input_device(device)

#     f = get_saved_audio_file(output_file_path)

#     start_time = time.time()

#     first_flag = True
#     while True:
#         l, data = inp.read()
#         if first_flag:
#             first_flag = False
#             start_time = time.time()
#         if l:
#             f.writeframes(data)
#             time.sleep(.001)
#             # saves exactly time ms
#         if time.time() - start_time > record_time:
#             break
#     f.close()

#     return output_file_path

def open_audio_file(path):
    path = str(path)
    try:
        f = wave.open(path, "rb")
        print(f'Output File: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    except wave.Error as e:
        print(e)
        return None

    return f

# def play_audio(path, device="default"):
#     f = open_audio_file(path)
#     if f is None:
#         return False # failed to play

#     # 8bit is unsigned in wav files
#     if f.getsampwidth() == 1:
#         format = alsaaudio.PCM_FORMAT_U8
#     # Otherwise we assume signed data, little endian
#     elif f.getsampwidth() == 2:
#         format = alsaaudio.PCM_FORMAT_S16_LE
#     elif f.getsampwidth() == 3:
#         format = alsaaudio.PCM_FORMAT_S24_LE
#     elif f.getsampwidth() == 4:
#         format = alsaaudio.PCM_FORMAT_S32_LE
#     else:
#         raise ValueError('Unsupported format')

#     periodsize = f.getframerate() // 8

#     out = alsaaudio.PCM(channels=f.getnchannels(),
#                            rate=f.getframerate(),
#                            format=format,
#                            periodsize=periodsize,
#                            device=device)
#     data = f.readframes(periodsize)
#     while data:
#         # Read data from stdin
#         out.write(data)
#         data = f.readframes(periodsize)

#     f.close()
#     return True

import pyaudio
# Setup channel info
FORMAT = pyaudio.paInt16 # data type formate
CHANNELS = 1 # Adjust to your number of channels
RATE = 16000 # Sample Rate
CHUNK = 1024 # Block Size
WAVE_OUTPUT_FILENAME = "out.wav"

def record_audio_by_time(output_file_path, device="default", record_time=10):
    # Startup pyaudio instance
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK, input_device_index=1)
    frames = []

    # Record for RECORD_SECONDS
    for i in range(0, int(RATE / CHUNK * record_time)):
        data = stream.read(CHUNK)
        frames.append(data)


    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Write your new .wav file with built in Python 3 Wave module
    waveFile = wave.open(output_file_path, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def play_audio(path, device="default"):
    f = open_audio_file(path)
    if f is None:
        return False # failed to play
    
    audio = pyaudio.PyAudio()
    stream = audio.open(format =
                audio.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True)
    
    data = f.readframes(CHUNK)

    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = f.readframes(CHUNK)


    # cleanup stuff.
    f.close()
    stream.close()    
    audio.terminate()
    return True


if __name__ == "__main__":
    record_audio_by_time("out.wav")
    play_audio("out.wav")
