import random
from pathlib import Path
import shutil
from dotenv import load_dotenv
import os

from llm_handler import LLM
import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp
import audio_management as am

import helper as h
from helper import timeit
from constants import *

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve())

# Maunally load environment variables from the .env file
load_dotenv(DOTENV_PATH)

#TODO: HANDLE TERMINATIONS
#TODO: STREAM LLM OUTPUT

class GameServer:
    def __init__(self,
                 temp_dir_path=TEMP_DIR,
                 prompts_json_path=PROMPTS_JSON_PATH,
                 server_ip=os.getenv("SERVER_IP"),
                 server_port=os.getenv("SERVER_PORT"),
                 remove_temp=True):
        # general file init``
        self.temp_dir = h.init_temp_storage(temp_dir_path)
        self.remove_temp = remove_temp
        self.prompts = h.read_prompts_json(prompts_json_path)

        # # file transfer setup
        self.fts = tcp.FileTransferServer(server_ip, server_port)

        self.llm = LLM(os.getenv("KEY"))

        self.use_local = True # flag if server isnt started to run a local version for debugging/testing

    def start_server(self):
        self.fts.start_server() # blocks until a client connects
        self.use_local = False

    def initiate_game(self):
        # getting the players name
        user_name = self.prompt_and_response_non_stream("system", self.prompts["init"])

        # prompting user for the story setting
        story_setting = self.prompt_and_response_non_stream("user", user_name)

        return story_setting

    def prompt_and_response_non_stream(self, role="user", prompt=None):
        llm_res = self.prompt_llm_non_stream(role, prompt)
        self.send_client_tts(llm_res)
        client_res = self.get_client_response_non_stream()

        return client_res

    def prompt_llm_non_stream(self, role="user", prompt=None):
        if prompt is None: # no prompt ie prob didnt get a response
            res = "Sorry I didn't catch that. Could you say that again?"
        else:
            res = timeit(self.llm.prompt_llm_non_stream)(role=role, prompt=prompt) # initialization prompt

        return res

    def send_client_tts(self, audio_text):
        # play some audio to client
        temp_wav_path = self.temp_dir / "temp.wav"
        temp_wav_path = tba.convert_text_to_bear_audio_opt(audio_text, temp_wav_path, self.temp_dir)
        if not self.use_local:
            self.fts.send_file(temp_wav_path)
        else:
            am.play_audio(temp_wav_path)
            print(f"ChatGPT says: {audio_text}")

    def get_client_response_non_stream(self):
        # get a client wav message and process
        if not self.use_local:
            # client should get stuff here
            client_wav_path = self.temp_dir / "client_res.wav"
            client_wav_path = self.fts.receive_file(client_wav_path)
            client_res = timeit(sp.recognize_wav)(client_wav_path)

            print(f"You say: {client_res}")
        else: # local mode that just takes a user input
            client_res = input("You respond: ")

        return client_res

    def main_loop_non_stream(self, initial_prompt):
        prompt = initial_prompt

        # Variables for the game logic
        random_round_next_round = False
        random_round = False
        while True:
            llm_response = self.prompt_llm_non_stream(prompt=prompt)
            self.send_client_tts(llm_response)
            if "for playing" in llm_response:
                print("Game is over!")
                # send termination signal here
                break

            prompt = self.get_client_response_non_stream()

        if random_round_next_round:
            random_round = True
            random_round_next_round = False

        # 10% chance of a potentially game ending round
        if random.randint(1,10) == 1:
            print("It's random time")
            self.llm.add_chat_history("system", self.prompts["next_round_random"])
            random_round_next_round = True

        # If this is a random round, we use randomness to determine if the child keeps playing or not
        if random_round and random.randint(1,3) == 2:
            print("FAILURE")
            self.llm.add_chat_history("system", self.prompts["failure"])
            random_round = False
        else:
            random_round_next_round = False
            random_round = False

    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():
    game_server = GameServer()
    game_server.start_server()
    story_setting = game_server.initiate_game()
    game_server.main_loop_non_stream(story_setting)

if __name__ == '__main__':
    main()
