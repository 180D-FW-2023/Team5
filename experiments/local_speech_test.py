
# new file without any rbp drivers to test on local systems

import sys
import os
sys.path.append(r"../src")

import speech_to_text as stt
import text_to_speech as tts
import helper as h


def local_testing():
    temp_dir = h.init_temp_storage(temp_dir_path)
    temp_wav_file = "../test_data/test_capstone.wav"
    text = h.timeit(stt.recognize_wav)(temp_wav_file)
    out_audio_path = h.timeit(tts.convert_text_to_bear_audio_opt)(text, "out.wav", temp_dir)
    print(out_audio_path)


if __name__ == "__main__":
    local_testing()
