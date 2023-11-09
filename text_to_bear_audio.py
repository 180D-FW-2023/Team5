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

from gtts import gTTS
from pydub import AudioSegment
import numpy as np
from numpy.random import uniform
import wave
import os

def convert_text_to_bear_audio(input_text):
    int_dir = "./intermediate_files"
    out_dir = "./output"

    # Create the intermediate directory if it doesn't already exist
    if not os.path.exists(int_dir):
        os.makedirs(int_dir)

    # Create the output directory if it doesn't already exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    audio_mp3_path = int_dir + "/raw_audio.mp3"
    audio_wav_path = int_dir + "/raw_audio.wav"

    # Text-to-speech and save as WAV
    tts = gTTS(input_text)
    tts.save(audio_mp3_path)

    # Convert MP3 to WAV using PyDub
    audio = AudioSegment.from_mp3(audio_mp3_path)
    audio.export(audio_wav_path, format="wav")

    # Read in raw wave file
    sound = AudioSegment.from_file(audio_wav_path, format=audio_wav_path[-3:])

    # Shift the audio up
    octaves = 0.4
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(44100)

    # Export pitch-changed sound
    hipitch_sound.export(out_dir + "/bear_voice.wav", format="wav")

    # Remove the intermediate directory
    os.remove(audio_mp3_path)
    os.remove(audio_wav_path)
    os.rmdir(int_dir)

if __name__ == '__main__':

    input_text = "Hi there! What's your name? My name is foo foo the bear. Would you like to play a choose your own adventure game?"

    convert_text_to_bear_audio(input_text)