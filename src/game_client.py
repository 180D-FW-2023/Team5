import helper as h
import tcp_file_transfer as tcp
import rbp_drivers.wm8960_helpers as rbp
import os
from pathlib import Path
from dotenv import load_dotenv
import shutil
import time

from constants import *

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
                 remove_temp=True):
        self.temp_dir = h.init_temp_storage(temp_dir_path)

        self.remove_temp = remove_temp

        self.record_time = record_time
        
        #  client setup
        self.ftc = tcp.FileTransferClient(server_ip, server_port) # connects to server in init
        self.ftc.connect_to_server()
    
    def main_loop_non_stream(self):
        while True:
            received_file_path = str(self.temp_dir / "received.wav")
            self.ftc.receive_file(received_file_path)
            rbp.play_audio(received_file_path)
            record_file_path = str(self.temp_dir / "recorded.wav")
            time.sleep(.5)
            record_file_path = rbp.record_audio_by_time(record_file_path)
            self.ftc.send_file(record_file_path)

    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():
    game_client = GameClient()
    game_client.main_loop_non_stream()


if __name__ == '__main__':
    main()