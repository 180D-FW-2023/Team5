import os
import shutil
from pathlib import Path

from dotenv import load_dotenv

import helper as h
import tcp_file_transfer as tcp
import audio_management as am
from constants import *

from threading import Thread

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve())

# Maunally load environment variables from the .env file
load_dotenv(DOTENV_PATH)

class GameClient:
    def __init__(self,
                 temp_dir_path=TEMP_DIR,
                 server_ip=os.getenv("SERVER_IP"),
                 server_port=os.getenv("SERVER_PORT"),
                 record_time=RECORD_TIME,
                 remove_temp=False):
        self.temp_dir = h.init_temp_storage(temp_dir_path)

        self.remove_temp = remove_temp

        self.record_time = record_time

        #  client setup
        self.ftc = tcp.FileTransferClient(server_ip, server_port) # connects to server in init
        self.ftc.connect_to_server()

    def main_loop_non_stream(self):
        while True:
            received_file_path = self.temp_dir / "received.wav"

            received_file_path = self.ftc.receive_file(received_file_path)
            if received_file_path is None: # handles bad inputs
                break

            # am.play_audio(received_file_path)
            Thread(target=lambda x: am.play_audio(received_file_path)).start()

            record_file_path = self.temp_dir / "recorded.wav"

            # record_file_path = am.record_audio_by_time(record_file_path)
            Thread(target=lambda x: am.record_audio_by_time(record_file_path)).start()
            self.ftc.send_file(record_file_path)

            os.remove(received_file_path)
            os.remove(record_file_path)


    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():
    game_client = GameClient()
    game_client.main_loop_non_stream()


if __name__ == '__main__':
    main()
