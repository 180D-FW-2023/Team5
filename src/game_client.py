

import os
import sys
import shutil
from pathlib import Path
import queue
from dotenv import load_dotenv
import threading
import time
import argparse
import pyaudio

from signals import Signals
import helper as h
import tcp_file_transfer as tcp
import play_and_record_audio as am
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
                 remove_temp=True,
                 subprocess_mode=True,
                 use_imu = True,
                 imu_use_threading = False):
        self.temp_dir = h.init_temp_storage(temp_dir_path)

        self.remove_temp = remove_temp

        self.record_time = record_time

        self.subprocess_mode = subprocess_mode # uses subprocessing to call alsaaudio for audio calls

        self.imu_use_threading = imu_use_threading

        #  client setup
        print(server_ip)
        print(server_port)
        self.tcpc = tcp.TCPClient(server_ip, server_port) # connects to server in init
        self.tcpc.connect_to_server()
        
        self.use_imu = use_imu

        if self.use_imu:
            from imu.imu_handler import ImuHandler
            self.imu = ImuHandler()
            self.imu_enabled = self.imu.imu_enabled

        if self.subprocess_mode == False:
            global audio
            audio = pyaudio.PyAudio()
        else:
            audio = None


    def main_loop(self):
        output_queue = queue.Queue(maxsize=10)

        imu_round = False
        imu_shake_round = False
        collect_imu_data = False
        detect_shake = False
        record = False
        start_time = 0

        while True:

            if self.use_imu:
                if not self.imu_enabled: # disables imu if not enabled already
                    imu_round = False
                    imu_shake_round = False

            signal = self.tcpc.receive_signal()

            if signal == Signals.IMU_ROUND:
                imu_round = True
            
            elif signal == Signals.IMU_SHAKE_ROUND:
                imu_shake_round = True

            elif signal == Signals.INIT_FT_STREAMED:

                # separate thread for audio playback
                audio_playback_thread = threading.Thread(target=am.play_audio_stream,
                                                    args=(output_queue, self.subprocess_mode, audio),
                                                        daemon=True)
                audio_playback_thread.start()
                self.tcpc.receive_file_stream(output_queue, self.temp_dir / "playback", ".wav", file_name_tag="playback")

                audio_playback_thread.join() # wait for playback to finish

                if imu_round:
                    collect_imu_data = True
                elif imu_shake_round:
                    detect_shake = True
                record = True

            elif signal == Signals.GAME_END:
                print("Game Ended. Closing Client")
                sys.exit(0)
            
            elif signal == Signals.RETRY_IMU:
                # We need to retry collecting IMU data
                collect_imu_data = True
                print("Retrying imu now")
                signal = self.tcpc.receive_signal()
                if signal != Signals.FILE_SENT:
                    print("Error: received other signal before audio file.")
                    sys.exit(1)

                received_file_path = self.temp_dir / "received.wav"

                received_file_path = self.tcpc.receive_file(received_file_path)
                if received_file_path is None: # handles bad inputs
                    break
                am.play_audio(received_file_path)
                os.remove(received_file_path)

            else:
                # TODO: Handle other signals
                raise NotImplementedError(f"Signal {Signals(signal).name} is not implemented")

            # Determine if toy is moved left/right
            if collect_imu_data:
                imu_round = False

                print("IMU round.")

                if self.use_imu:
                    if self.imu_use_threading:
                        imu_thread = threading.Thread(target=self.imu.collect_imu_data_wrapper, daemon=True)
                        imu_thread.start()
                        if self.imu.res_queue.get(timeout=5) == False:
                            print("\nleft left left left\n")
                            self.tcpc.send_signal(Signals.IMU_TURN_LEFT)
                        else:
                            print("\nright right right right\n")
                            self.tcpc.send_signal(Signals.IMU_TURN_RIGHT)
                        
                        imu_thread.join()

                    else:
                        imu_res = self.imu.collect_imu_data()
                        if imu_res == False:
                            print("\nleft left left left\n")
                            self.tcpc.send_signal(Signals.IMU_TURN_LEFT)
                        elif imu_res == True:
                            print("\nright right right right\n")
                            self.tcpc.send_signal(Signals.IMU_TURN_RIGHT)
                        # Return value was None
                        else:
                            print("\nno turn detected\n")
                            self.tcpc.send_signal(Signals.IMU_NO_TURN)
                else: #hardcoded response if we aren't using the IMU
                    self.tcpc.send_signal(Signals.IMU_TURN_RIGHT)

            # Determine if toy is shook
            if detect_shake:

                imu_shake_round = False

                print("IMU shake round.")

                if self.use_imu:
                    imu_res = self.imu.detect_shake()
                    if imu_res:
                        print("Shake detected")
                        self.tcpc.send_signal(Signals.IMU_SHAKE)
                    else:
                        print("No shake detected")
                        self.tcpc.send_signal(Signals.IMU_NO_SHAKE)
                else: # hardcoded response if we aren't using the IMU
                    self.tcpc.send_signal(Signals.IMU_SHAKE)

            # Normal round; record audio
            elif record:
                record_file_path = self.temp_dir / "recorded.wav"

                record_file_path = am.record_audio_by_time(record_file_path, subprocess_mode=self.subprocess_mode, audio=audio)
                self.tcpc.send_file(record_file_path)
                start_time = time.time()
                print(f"\nJust sent server file; starting time: {start_time}\n")

                os.remove(record_file_path)
            
            collect_imu_data = False
            detect_shake = False
            record = False

    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():
    parser = argparse.ArgumentParser(description='Game client program for the choose your own adventure game.')
    parser.add_argument('-ns', action='store_false', help='No subprocess mode (do not play audio via alsa audio subprocess, instead use pygame) ')
    parser.add_argument('-ni', action='store_false', help='Do NOT use the IMU')

    args = parser.parse_args()
    subprocess_mode = args.ns
    use_imu = args.ni

    game_client = GameClient(subprocess_mode=subprocess_mode, use_imu=use_imu)
    game_client.main_loop()


if __name__ == '__main__':
    main()