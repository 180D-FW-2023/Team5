import sys
import os
sys.path.append(r"../src")

import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp

from helper import timeit

RECEIVED_FILE_PATH = "temp.wav"

fts = tcp.FileTransferServer("192.168.99.31", 12345)
fts.start_server()

fts.receive_file(RECEIVED_FILE_PATH)

text = timeit(sp.recognize_wav)(RECEIVED_FILE_PATH)
out_audio_path = timeit(tba.convert_text_to_bear_audio_opt)(text, "out.wav")
os.remove(RECEIVED_FILE_PATH)
print(out_audio_path)

fts.send_file(out_audio_path)
os.remove(out_audio_path)

print("Server Finished")
