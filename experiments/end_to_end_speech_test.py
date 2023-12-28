import sys
import os
sys.path.append(r"../src")

import wm8960_helpers as rbp
import speech_processing as sp
import text_to_bear_audio as tba
from helper import timeit

def edge_testing():
    temp_wav_file = "out.wav"
    timeit(rbp.record_audio_by_time)(temp_wav_file, record_time=10)
    text = timeit(sp.recognize_wav)(temp_wav_file)

    os.remove(temp_wav_file)

    out_audio_path = timeit(tba.convert_text_to_bear_audio)(text, 1)
    print(out_audio_path)
    timeit(rbp.play_audio)(out_audio_path)

if __name__ == "__main__":
    edge_testing()
