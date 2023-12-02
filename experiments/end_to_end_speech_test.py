import sys
sys.path.append(r"/home/pi/Team5/src")

import rbp_drivers.wm8960_helpers as rbp
import speech_processing as sp
import text_to_bear_audio as tba

import time # timing tests



# helper function to test timings
def timeit(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        run_time = end_time - start_time
        print(f"Function {func.__name__} took {run_time:.6f} seconds to run.")
        return result
    return wrapper

def main():
    temp_wav_file = "out.wav"
    timeit(rbp.record_audio_by_time)(temp_wav_file, record_time=10)
    text = timeit(sp.recognize_wav)(temp_wav_file)

    out_audio_path = timeit(tba.convert_text_to_bear_audio)(text)
    print(out_audio_path)
    timeit(rbp.play_audio)(out_audio_path)




if __name__ == "__main__":
    main()
