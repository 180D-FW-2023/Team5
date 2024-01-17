import random
from pathlib import Path
import shutil
from dotenv import load_dotenv
import os
import time
import argparse
from llm_handler import LLM
import speech_to_text as sp
import text_to_speech as tba
import tcp_file_transfer as tcp
import play_and_record_audio as am
from signals import Signals
import helper as h
from helper import timeit
from constants import *

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve())

# Maunally load environment variables from the .env file
load_dotenv(DOTENV_PATH)

#TODO: HANDLE TERMINATIONS

class GameServer:
    def __init__(self,
                 use_local,
                 temp_dir_path=TEMP_DIR,
                 prompts_json_path=PROMPTS_JSON_PATH,
                 server_ip=os.getenv("SERVER_IP"),
                 server_port=os.getenv("SERVER_PORT"),
                 remove_temp=True,
                 stream_llm=True):
        
        # general file init
        self.temp_dir = h.init_temp_storage(temp_dir_path)
        self.remove_temp = remove_temp
        self.prompts = h.read_prompts_json(prompts_json_path)

        # file transfer setup
        self.tcps = tcp.TCPServer(server_ip, server_port)

        # init LLM handler
        self.llm = LLM(os.getenv("KEY"), stream=stream_llm)

        self.use_local = use_local # flag if server isnt started to run a local version for debugging/testing
        print(f"LOCAL DEBUGGING SET TO: {use_local}")

    def start_server(self):
        print("start server here")
        print(self.use_local)
        self.tcps.start_server() # blocks until a client connects

    def init_game(self):
        # getting the players name
        user_name = self.execute_single_game_round("system", self.prompts["init"])
        
        # prompting user for the story setting
        story_setting = self.execute_single_game_round("user", user_name)

        return story_setting

    def convert_and_send_llm_response(self):
        # sends the actual message since its in a queue thats buffering over time
        chunks = []
        role = None

        # first signal indicated the start of a streamed message
        # note: as of now, the only signal that matters on the client end is INIT_FT_STREAMED -Spencer
        self.tcps.send_signal(Signals.INIT_FT_STREAMED)
        first_message = True
        start = time.time()
        while True:
            ret = self.llm.response_queue.get(timeout=10)
            if first_message:
                end = time.time()
                print(f"Delay to begin processing llm response: {end-start}")
                first_message = False
                
            if ret is None: # message is over
                break
            role, chunk = ret
            if chunk == "":
                continue
            chunks.append(chunk)
            self.convert_tts_and_send_client(chunk)
        
        # signals the end of a file stream
        self.tcps.send_signal(Signals.END_FT_STREAMED)

        # add to the chat history
        msg = "".join(chunks)
        self.llm.add_chat_history(role, msg) # update the llm chat history

        return msg

    def execute_single_game_round(self, role="user", prompt=None, force_response=True):
        # force response continues rerunning until you recognize a response

        prompt_successful = self.llm.prompt_llm(role, prompt)
        if not self.use_local:
            llm_res = self.convert_and_send_llm_response()

        print("what's your name")
        client_res = self.get_client_response()

        # locks and continuously asks for a new response
        while client_res is None and force_response:
            self.convert_tts_and_send_client("Sorry, I didn't catch that could you say that again?")
            client_res = self.get_client_response()

        return client_res

    def convert_tts(self, audio_text):
        # convert LLM response text to bear audio file
        temp_wav_path = self.temp_dir / f"temp_{int(time.time())}.wav"
        temp_wav_path = tba.convert_text_to_bear_audio_opt(audio_text, temp_wav_path, self.temp_dir)

        return temp_wav_path

    def convert_tts_and_send_client(self, audio_text):
        if audio_text == "": # don't attempt to send if nothing to send
            return
        
        temp_wav_path = self.convert_tts(audio_text)

        # check if we are just doing local debugging (no client)
        if not self.use_local:
            self.tcps.send_file(temp_wav_path)
        else:
            #am.play_audio(temp_wav_path)
            print(f"ChatGPT says: {audio_text}")

    def get_client_response(self):
        print("Waiting for client response")
        # get a client wav message and process
        if not self.use_local:
            # client should get stuff here
            client_wav_path = self.temp_dir / "client_res.wav"
            self.tcps.receive_signal(expected_signals=[Signals.FILE_SENT])
            client_wav_path = self.tcps.receive_file(client_wav_path)
            client_res = timeit(sp.recognize_wav)(client_wav_path)

            print(f"You said: {client_res}")
        else: # local mode that just takes a user input
            client_res = input("You respond: ")

        return client_res
    
    def main_loop(self, initial_prompt):
        prompt = initial_prompt

        # Variables for the game logic
        random_round_next_round = False
        random_round = False
        while True:
            self.llm.prompt_llm(prompt=prompt)
            llm_res = self.convert_and_send_llm_response()
            if "for playing" in llm_res:
                print("Game is over!")
                # send termination signal here
                break

            prompt = self.get_client_response()
            print("Got client response")

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

    parser = argparse.ArgumentParser(description='Game server program for the choose your own adventure game.')
    parser.add_argument('-d', action='store_true', help='Enable local debugging (i.e. do not use client)')

    args = parser.parse_args()

    # Access the arguments
    local_debug = args.d

    print(local_debug)

    game_server = GameServer(local_debug)
    print("created game server")
    print(game_server.use_local)
    if not game_server.use_local:
        game_server.start_server()
    print("started game server")
    story_setting = game_server.init_game()
    print("started game")
    game_server.main_loop(story_setting)

if __name__ == '__main__':
    main()
