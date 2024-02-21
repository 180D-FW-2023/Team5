

import os
import sys
import shutil
from pathlib import Path
import queue
from dotenv import load_dotenv
import threading
import time

from signals import Signals
import helper as h
import tcp_file_transfer as tcp
import play_and_record_audio as am
from constants import *

from imu.imu_handler import ImuHandler

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
                 remove_temp=True,
                 subprocess_mode=True):
        self.temp_dir = h.init_temp_storage(temp_dir_path)

        self.remove_temp = remove_temp

        self.record_time = record_time

        self.subprocess_mode = subprocess_mode # uses subprocessing to call alsaaudio for audio calls

        #  client setup
        self.tcpc = tcp.TCPClient(server_ip, server_port) # connects to server in init
        self.tcpc.connect_to_server()

        self.imu = ImuHandler()
        self.imu_enabled = self.imu.imu_enabled


    def main_loop(self):
        output_queue = queue.Queue(maxsize=10)

        imu_round = False
        imu_round_now = False

        while True:
            if not self.imu_enabled: # disables imu if not enabled already
                imu_round = False

            signal = self.tcpc.receive_signal()
            if signal == Signals.FILE_SENT:
                received_file_path = self.temp_dir / "received.wav"

                received_file_path = self.tcpc.receive_file(received_file_path)
                if received_file_path is None: # handles bad inputs
                    break
                am.play_audio(received_file_path)
                os.remove(received_file_path)
            elif signal == Signals.INIT_FT_STREAMED:
                # separate thread for audio playback
                audio_playback_thread = threading.Thread(target=am.play_audio_stream,
                                                    args=(output_queue, self.subprocess_mode, ),
                                                        daemon=True)
                audio_playback_thread.start()
                self.tcpc.receive_file_stream(output_queue, self.temp_dir / "playback", ".wav", file_name_tag="playback")
                audio_playback_thread.join() # wait for playback to finish
                # shutil.rmtree(self.temp_dir / "playback")
                if imu_round:
                    imu_round_now = True
                    imu_round = False
            elif signal == Signals.GAME_END:
                print("Game Ended. Closing Client")
                sys.exit(0)
            # IMU_ROUND signal should be sent after playback finishes
            elif signal == Signals.IMU_ROUND:
                imu_round = True
                continue
            else:
                # TODO: Handle other signals
                raise NotImplementedError(f"Signal {Signals(signal).name} is not implemented")

            if imu_round_now:
                print("IMU round. ")
                if self.imu.collect_imu_data() == False:
                    print("\nleft left left left\n")
                    self.tcpc.send_signal(Signals.IMU_TURN_LEFT)
                else:
                    print("\nright right right right\n")
                    self.tcpc.send_signal(Signals.IMU_TURN_RIGHT)
                imu_round_now = False
            else:
                record_file_path = self.temp_dir / "recorded.wav"
                #time.sleep(AUDIO_SWITCH_DELAY)
                record_file_path = am.record_audio_by_time(record_file_path, subprocess_mode=self.subprocess_mode)
                self.tcpc.send_file(record_file_path)

                os.remove(record_file_path)


    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():
    game_client = GameClient()
    game_client.main_loop()


if __name__ == '__main__':
    main()