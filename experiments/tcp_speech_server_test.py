import sys
import os
sys.path.append(r"../src")

import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp

from helper import timeit

fts = tcp.FileTransferServer("192.168.99.31", 12345)
fts.start_server()

receive_file_path = "temp.wav"
fts.receive_file(receive_file_path)

text = timeit(sp.recognize_wav)(receive_file_path)
out_audio_path = timeit(tba.convert_text_to_bear_audio_opt)(text, "out.wav")
os.remove(receive_file_path)
print(out_audio_path)

fts.send_file(out_audio_path)

print("received")
