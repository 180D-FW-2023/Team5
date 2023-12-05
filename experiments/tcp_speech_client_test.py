import sys
sys.path.append(r"../src")
import os
import time

import tcp_file_transfer as tcp
import rbp_drivers.wm8960_helpers as rbp
from helper import timeit

INPUT_FILE_PATH = "../test_data/test_capstone.wav"
RECEIVED_PATH = "out.wav"

start = time.time()
ftc = tcp.FileTransferClient() # uses defaults in environment
ftc.connect_to_server()
ftc.send_file(INPUT_FILE_PATH)
ftc.receive_file(RECEIVED_PATH)
end = time.time()

rbp.play_audio(RECEIVED_PATH)
os.remove(RECEIVED_PATH)

print(f"TOTAL PROCESSING TIME FOR FILE: {end-start}")
