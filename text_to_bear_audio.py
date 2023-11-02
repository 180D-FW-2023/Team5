##################################################################################################################
#
#           Text string to teddy bear voice converter
#           Written by Spencer Stice
#           Sources: https://batulaiko.medium.com/how-to-pitch-shift-in-python-c59b53a84b6d
#           Requirements: gtts, pydub, numpy, wave, os
#           Note: if trouble with pydub occurs, install ffmpeg and add:
#           os.environ["FFMPEG_BINARY"] = r"path to ffmpeg.exe"
#
#
###################################################################################################################

input_text = "Hi there! What's your name? My name is foo foo the bear. Would you like to play a choose your own adventure game?"

from gtts import gTTS
from pydub import AudioSegment
import numpy as np
from numpy.random import uniform
import wave
import os

int_dir = "intermediate_files"
out_dir = "output"

# Check if the directory already exists
if not os.path.exists(int_dir):
    # If it doesn't exist, create the directory
    os.makedirs(int_dir)

if not os.path.exists(out_dir):
    # If it doesn't exist, create the directory
    os.makedirs(out_dir)

# Text-to-speech and save as WAV
tts = gTTS(input_text)
tts.save("./intermediate_files/raw_audio.mp3")

# Convert MP3 to WAV using PyDub
audio = AudioSegment.from_mp3("./intermediate_files/raw_audio.mp3")
audio.export("./intermediate_files/raw_audio.wav", format="wav")

#Read in raw wave file
filename = './intermediate_files/raw_audio.wav'
sound = AudioSegment.from_file(filename, format=filename[-3:])

#Shift the audio up
octaves = 0.4
new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
hipitch_sound = hipitch_sound.set_frame_rate(44100)

#export / save pitch changed sound
hipitch_sound.export(f"./output/bear_voice.wav", format="wav")