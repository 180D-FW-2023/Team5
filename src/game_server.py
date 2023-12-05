import random
from pathlib import Path

import helper as h

from llm_handler import LLM 
import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp
import os
import tcp_speech_server as tcpss

import sys
import json
import shutil

from dotenv import load_dotenv

from constants import *

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve()) 

# Maunally load environment variables from the .env file
load_dotenv(DOTENV_PATH)

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
        self.fts.start_server() # blocks until a client connects

        self.llm = LLM(os.getenv("KEY"))

    def initial_game_setup(self):
        # getting the players name
        user_name = self.prompt_and_response_non_stream("user", self.prompts["init"])
        
        # prompting user for the story setting
        story_setting = self.prompt_and_response_non_stream("user", user_name)
        
        return story_setting

    def prompt_and_response_non_stream(self, role="user", prompt=None):
        # prompt chat gpt, get response, send to client server, return client response
        res = self.llm.prompt_llm_non_stream(role="system", prompt=prompt) # initialization prompt
        temp_wav_path = str(self.temp_dir / "temp.wav")
        temp_wav_path = tba.convert_text_to_bear_audio_opt(res, temp_wav_path)
        
        self.fts.send_file()
        
        # client should get stuff here
        client_wav_path = str(self.temp_dir / "client_res.wav")
        client_wav_path = self.fts.receive_file(client_wav_path)
        client_res = h.timeit(sp.recognize_wav)(client_wav_path)

        print(f"You said: {client_res}")

        return client_res

    def get_client_package(self):
        self.fts.receive_file()

    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)


def main():

    game_server = GameServer()
    game_server.initial_game_setup()
    # ROUND 1: GET NAME
    # Add initial prompt to game state

    # # Send initial request to GPT 3.5 Turbo to get the game started
    # LLM_reponse = llm_h.send_openai_api_request_and_convert_and_play(game_state, fts)
    # game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

    # speech = h.timeit(sp.recognize_wav)(RECEIVED_FILE_PATH)
    # os.remove(RECEIVED_FILE_PATH)
    # print("you said: " + speech)

    # game_state.append(llm_h.create_game_state_addition("user", speech))
    # LLM_reponse = llm_h.send_openai_api_request_and_convert_and_play(game_state, fts)
    # game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

    # speech = h.timeit(sp.recognize_wav)(RECEIVED_FILE_PATH)
    # os.remove(RECEIVED_FILE_PATH)
    # print("you said: " + speech)
    # game_state.append(llm_h.create_game_state_addition("user", speech))

    # # ROUND 2: CHOOSE STORY SETTING
    # LLM_reponse = llm_h.send_openai_api_request_and_convert_and_play(game_state, fts)
    # game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))
    # speech = h.timeit(sp.recognize_wav)(RECEIVED_FILE_PATH)
    # os.remove(RECEIVED_FILE_PATH)
    # print("you said: " + speech)
    # game_state.append(llm_h.create_game_state_addition("user", speech))
    
    # # Variables for the game logic
    # random_round_next_round = False
    # random_round = False

    # # ROUNDS 3+: MAIN GAME LOOP
    # while True:

    #     # Get current round's story output
    #     LLM_reponse = llm_h.send_openai_api_request_and_convert_and_play(game_state, fts)

    #     # Game is over, stop asking for reponses from the child
    #     if "for playing" in LLM_reponse:
    #         break

    #     game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

    #     speech = h.timeit(sp.recognize_wav)(RECEIVED_FILE_PATH)
    #     os.remove(RECEIVED_FILE_PATH)
    #     print("you said: " + speech)

    #     # The child has a chance of losing the game this round
    #     if random_round_next_round:
    #         random_round = True
    #         random_round_next_round = False

    #     # 10% chance of a potentially game ending round
    #     if random.randint(1,10) == 1:
    #         print("It's random time")
    #         speech += """ (Also, for this round only, present THREE options and MAKE IT CLEAR that one of them
    #         is game ending. If the child chooses this option they will lose the game. Don't assume they know that one option will lose
    #         them the game (i.e. don't say 'remember')."""
    #         random_round_next_round = True

    #     # If this is a random round, we use randomness to determine if the child keeps playing or not
    #     if random_round and random.randint(1,3) == 2:
    #         speech += """ (By the way, the child chose the wrong option this round so the game should end. Come up with a kid friendly 
    #                     reason why the child lost the game and tell them thanks for playing. Don't start the response by saying great 
    #                     job, since they lost game.)
    #                     """
    #         random_round = False

    #     game_state.append(llm_h.create_game_state_addition("user", speech))



if __name__ == '__main__':
    main()