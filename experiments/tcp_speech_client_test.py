import sys
import os
sys.path.append(r"../src")

import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp

from helper import timeit

wav_file = "../test_data/test_capstone.wav"

ftc = tcp.FileTransferClient("192.168.99.31", 12345)
ftc.connect_to_server()
ftc.send_file(wav_file)
ftc.receive_file("out.wav")
print("received")
