import sys
import os
sys.path.append(r"../src")

import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp

from helper import timeit

RECEIVED_FILE_PATH = "temp.wav"

SERVER_IP = "127.0.0.1"

FIRST = True

def init_server():
    fts = tcp.FileTransferServer(SERVER_IP, 12345)
    fts.start_server()
    return fts

def send_bear_audio_and_receive_raw_audio(bear_audio_path, fts, end=False):

    fts.send_file(bear_audio_path)
    os.remove(bear_audio_path)

    if end:
        fts.send_file("./termination.txt")
        fts.receive_file(RECEIVED_FILE_PATH)
        print("received file-----------------------")
