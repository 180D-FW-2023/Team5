import speech_processing as sp
import text_to_bear_audio as tba
import stream_test as st
import llm_handler as llm_h
import random
from helper import timeit
import tcp_speech_client as tcpcl
import rbp_drivers.wm8960_helpers as rbp
import tcp_file_transfer as tcp
import rbp_drivers.wm8960_helpers as rbp
import os
import threading
import wave

#Sets the record time (in seconds) when the RPI listens to the child
RECORD_TIME = 10

#IP Address of the TCP server for handling most computation tasks
SERVER_IP = "192.168.99.31"

def main():

    ftc = tcp.FileTransferClient(SERVER_IP, 12345)
    ftc.connect_to_server()

    while True:

        received_file = "received_path.wav"
        ftc.receive_file("received_path.wav")

        try:
            with wave.open(received_file, 'rb') as wav_file:
                # Check if the file is a valid WAV file
                if wav_file.getnchannels() > 0:
                    rbp.play_audio(received_file)
                    os.remove(received_file)

        except wave.Error:
            # An error occurred, so it's not a valid WAV file
            os.remove(received_file)

            ftc.send_file("./test_capstone.wav")



if __name__ == '__main__':
    main()