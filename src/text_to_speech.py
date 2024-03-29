##################################################################################################################
#
#           Text string to teddy bear voice converter
#           Written by Spencer Stice and Nick Brandis
#           Sources: https://batulaiko.medium.com/how-to-pitch-shift-in-python-c59b53a84b6d
#           Requirements: gtts, pydub, numpy, wave, os
#           Note: if trouble with pydub occurs, install ffmpeg and add:
#           os.environ["FFMPEG_BINARY"] = r"path to ffmpeg.exe"
#
#
###################################################################################################################

import os
import time
import threading
import shutil

#os.environ["FFMPEG_BINARY"] = r"C:\ffmpeg-2023-12-04-git-8c117b75af-full_build\ffmpeg-2023-12-04-git-8c117b75af-full_build\bin\ffmpeg.exe"

import ffmpeg
from gtts import gTTS
from pydub import AudioSegment

from helper import timeit
from constants import *

import subprocess
import re

def play_wav(wav_path):
    cmd = "aplay -D hw:3,0 -f S16_LE -c2 " + wav_path
    # Run the command in the background
    process = subprocess.Popen(cmd, shell=True)
    process.wait()

# # Use pygame to play a wav file using default speaker
# def play_wav(wav_path):
# # Create a lock to synchronize access to the audio playback
#     import pygame
#     audio_lock = threading.Lock()
#     pygame.init()
#     pygame.mixer.init()

#     with audio_lock:

#         try:
#             sound = pygame.mixer.Sound(wav_path)
#             sound.play()
#             # Wait for the sound to finish playing
#             pygame.time.wait(int(sound.get_length() * 1000))
#         except Exception as e:
#             print(f"Error: {e}")

# Split a long string with no punctuation into two pieces based on
# words that sound natural with a pause before them
def split_into_two_pieces(input_string):
    # First look for conjunctions
    conjunctions = [' or ', ' and ', ' but ']
    for conjunction in conjunctions:
        if conjunction in input_string:
            pieces = input_string.split(conjunction, 1)
            return pieces[0].strip(), conjunction + pieces[1]
    # If none found, look for other words
    second_options = ['that', 'with', 'then']
    for word in second_options:
        if word in input_string:
            pieces = input_string.split(word, 1)
            return pieces[0].strip(), word + pieces[1]
    return None


# Invalid strings are None, empty string, or don't have any letters
def text_str_valid(input_str):
    if input_str == None or input_str == "":
        return False 
    return bool(re.search(r'[a-zA-Z]', input_str))

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

    # Create an empty audio segment to store the audio content
    final_audio = AudioSegment.silent(duration=0)

    text_pieces = [input_text]

    # If number of chars is over 100, we have to split the text to create a more natural pause
    #print("INPUT TEXT NUM CHARS: ", len(input_text))
    if len(input_text) > 100:
        res = split_into_two_pieces(input_text)
        if res != None:
            text_pieces = res

    for text_piece in text_pieces:
        # Text-to-speech and save as WAV
        start = time.time()
        tts = gTTS(text_piece)
        end = time.time()
        print(f"TTS: {end-start}")
        tts.save(audio_mp3_path)

        # Convert MP3 to WAV using PyDub
        audio = AudioSegment.from_mp3(audio_mp3_path)
        final_audio += audio

    final_audio.export(audio_wav_path, format="wav")

    # Read in raw wave file
    sound = AudioSegment.from_file(audio_wav_path, format=audio_wav_path[-3:])

    # Shift the audio up
    octaves = 0.4
    new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    hipitch_sound = hipitch_sound.set_frame_rate(RATE)

    # Export pitch-changed sound
    pitch_change_path = out_dir + "/bear_voice_" + str(output_path_num) + ".wav"
    hipitch_sound.export(pitch_change_path, format="wav")

    # Remove the intermediate directory
    os.remove(audio_mp3_path)
    os.remove(audio_wav_path)

    shutil.rmtree(int_dir)

    return pitch_change_path

# Creates a bear voice wav file and plays it
# requires ffmpeg
def convert_text_to_bear_audio_opt(input_text,
                                   output_path,
                                   temp_dir_path,
                                   n_semitones=4,
                                   tempo_multiplier=1.2):

    temp_mp3_path = temp_dir_path / "tba_conversion.mp3"

    text_pieces = [input_text]

    # If number of chars is over 100, we have to split the text to create a more natural pause
    #print("INPUT TEXT NUM CHARS: ", len(input_text))
    if len(input_text) > 100:
        res = split_into_two_pieces(input_text)
        if res != None:
            text_pieces = res

    with open(temp_mp3_path, "wb") as f:
        for text_piece in text_pieces:
            # Text-to-speech and save as WAV
            # print("\nText piece", text_piece)
            # print(type(text_piece))    
            if text_str_valid(text_piece):
                tts = gTTS(text_piece)
                timeit(tts.write_to_fp)(f) # actual tts time

    # ffmpeg run
    pitch = (2**n_semitones)/12 # frequency ratio of a semitone

    stream = ffmpeg.input(temp_mp3_path,
                          y=None,
                          hide_banner=None,
                          loglevel="error"
                          ) # =None is an ffmpeg flag with no input kw
    # stream = stream.filter("rubberband",
    #                        pitch=pitch,
    #                        tempo=tempo_multiplier
    #                        )
    stream = stream.filter("atempo",
                           tempo=tempo_multiplier
                           )
    stream = stream.output(str(output_path),
                           preset="ultrafast",
                           acodec="pcm_s16le",
                           ar=RATE,
                           ac=CHANNELS
                           )
    ffmpeg.run(stream)

    # Remove the intermediate directory
    # os.remove(audio_mp3_path)
    # os.remove(audio_wav_path)

    return output_path

if __name__ == '__main__':

    input_text = "I eat pizza all the time do you"

    convert_text_to_bear_audio(input_text)
