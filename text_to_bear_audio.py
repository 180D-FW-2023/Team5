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
import pygame
import time
import threading

# Create a lock to synchronize access to the audio playback
audio_lock = threading.Lock()
pygame.init()
pygame.mixer.init()

# Use pygame to play a wav file using default speaker
def play_wav(wav_path):
    with audio_lock:

        try:
            sound = pygame.mixer.Sound(wav_path)
            sound.play()
            # Wait for the sound to finish playing
            pygame.time.wait(int(sound.get_length() * 1000))
        except Exception as e:
            print(f"Error: {e}")


# Creates a bear voice wav file and plays it
def convert_text_to_bear_audio(input_text, output_path_num):
    int_dir = "./intermediate_files"
    out_dir = "./output"

    # Create the intermediate directory if it doesn't already exist
    if not os.path.exists(int_dir):
        os.makedirs(int_dir)

    # Create the output directory if it doesn't already exist
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    audio_mp3_path = int_dir + "/raw_audio_ " + str(output_path_num) + ".mp3"
    audio_wav_path = int_dir + "/raw_audio_" + str(output_path_num) + ".wav"

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
    pitch_change_path = out_dir + "/bear_voice_" + str(output_path_num) + ".wav"
    hipitch_sound.export(pitch_change_path, format="wav")

    # Remove the intermediate directory
    os.remove(audio_mp3_path)
    os.remove(audio_wav_path)
    os.rmdir(int_dir)

    sound = pygame.mixer.Sound(pitch_change_path)
    return sound.get_length(), pitch_change_path

if __name__ == '__main__':

    input_text = "I eat pizza all the time do you"

    convert_text_to_bear_audio(input_text)