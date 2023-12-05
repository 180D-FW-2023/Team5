from __future__ import print_function

import time
import wave
import pyaudio

# Setup channel info
FORMAT = pyaudio.paInt16 # data type formate
CHANNELS = 1 # Adjust to your number of channels
RATE = 16000 # Sample Rate
CHUNK = 1024 # Block Size

def open_audio_file(path):
    path = str(path)
    try:
        f = wave.open(path, "rb")
        print(f'Output File: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    except wave.Error as e:
        print(e)
        return None

    return f

class Recorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()

        # start Recording
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                    frames_per_buffer=CHUNK)

    def __del__(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()

    def record_audio_by_time(self, output_file_path, record_time=10):
        frames = []

        # Record for RECORD_SECONDS
        for i in range(0, int(RATE / CHUNK * record_time)):
            data = self.stream.read(CHUNK)
            frames.append(data)


        # Stop Recording

        # Write your new .wav file with built in Python 3 Wave module
        waveFile = wave.open(output_file_path, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

        return output_file_path

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
    play_audio("out.wav")
