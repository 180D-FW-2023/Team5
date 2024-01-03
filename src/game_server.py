import random
from pathlib import Path
import shutil
from dotenv import load_dotenv
import os
import time

from llm_handler import LLM
import speech_processing as sp
import text_to_bear_audio as tba
import tcp_file_transfer as tcp
import audio_management as am
from signals import Signals
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
                 remove_temp=True,
                 stream_llm=True):
        # general file init``
        self.temp_dir = h.init_temp_storage(temp_dir_path)
        self.remove_temp = remove_temp
        self.prompts = h.read_prompts_json(prompts_json_path)

        # # file transfer setup
        self.tcps = tcp.TCPServer(server_ip, server_port)

        self.llm = LLM(os.getenv("KEY"), stream=stream_llm)

        self.use_local = True # flag if server isnt started to run a local version for debugging/testing

    def start_server(self):
        self.tcps.start_server() # blocks until a client connects
        self.use_local = False

    def initiate_game(self):
        # getting the players name
        user_name = self.prompt_and_response("system", self.prompts["init"])
        # prompting user for the story setting

        story_setting = self.prompt_and_response("user", user_name)

        return story_setting

    def send_llm_response_tts(self):
        # sends the actual message since its in a queue thats buffering over time
        chunks = []
        role = None

        # TODO: SEND A SiGNAL TO INDICATE a STREAMED INPUT
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
            self.send_client_tts(chunk)
        
        self.tcps.send_signal(Signals.END_FT_STREAMED) # signals the end of a file stream

        # add to the chat history
        msg = "".join(chunks)
        self.llm.add_chat_history(role, msg) # update the llm chat history

        return msg

    def prompt_and_response(self, role="user", prompt=None, force_response=True):
        # force response continues rerunning until you recognize a response

        prompt_successful = self.llm.prompt_llm(role, prompt)
        llm_res = self.send_llm_response_tts()

        client_res = self.get_client_response()

        # locks and continuously asks for a new response
        while client_res is None and force_response:
            self.send_client_tts("Sorry, I didn't catch that could you say that again?")
            client_res = self.get_client_response()

        return client_res

    def make_tts(self, audio_text):
        # play some audio to client
        temp_wav_path = self.temp_dir / f"temp_{int(time.time())}.wav"
        temp_wav_path = tba.convert_text_to_bear_audio_opt(audio_text, temp_wav_path, self.temp_dir)

        return temp_wav_path

    def send_client_tts(self, audio_text):
        if audio_text == "":
            return
        
        temp_wav_path = self.make_tts(audio_text)
        if not self.use_local:
            self.tcps.send_file(temp_wav_path)
        else:
            am.play_audio(temp_wav_path)
            print(f"ChatGPT says: {audio_text}")

    def get_client_response(self):
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
            llm_res = self.send_llm_response_tts()
            if "for playing" in llm_res:
                print("Game is over!")
                # send termination signal here
                break

            prompt = self.get_client_response()

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
    game_server.main_loop(story_setting)

if __name__ == '__main__':
    main()
