
# new file without any rbp drivers to test on local systems

import sys
import os
sys.path.append(r"../src")

import speech_processing as sp
import text_to_bear_audio as tba
from helper import timeit


def local_testing():
    temp_wav_file = "../test_data/test_capstone.wav"
    text = timeit(sp.recognize_wav)(temp_wav_file)
    out_audio_path = timeit(tba.convert_text_to_bear_audio_opt)(text, 1)
    print(out_audio_path)


if __name__ == "__main__":
    local_testing()
