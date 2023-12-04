import speech_processing as sp
import text_to_bear_audio as tba
import llm_handler as llm_h
import random
from helper import timeit
import tcp_file_transfer as tcp
import os
import threading
import wave

#Sets the record time (in seconds) when the RPI listens to the child
RECORD_TIME = 10

#IP Address of the TCP server for handling most computation tasks
SERVER_IP = "192.168.1.89"

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
                    tba.play_wav(received_file)
                    os.remove(received_file)

        except wave.Error:
            # An error occurred, so it's not a valid WAV file
            os.remove(received_file)

            temp_wav_file = "out.wav"
            timeit(rbp.record_audio_by_time)(temp_wav_file, record_time=RECORD_TIME)
            ftc.send_file(temp_wav_file)
            os.remove(temp_wav_file)



if __name__ == '__main__':
    main()