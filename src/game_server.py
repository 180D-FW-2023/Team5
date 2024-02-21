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
import sys
import re

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve())

# Maunally load environment variables from the .env file
load_dotenv(DOTENV_PATH)

def extract_option_number(input_string):
    # Use regular expression to find the first occurrence of a number in the string
    match = re.search(r'\b\d+\b', input_string)
    
    if match:
        # Extract and return the matched number as an integer
        return int(match.group())
    else:
        # Return None if no number is found in the input string
        return None

#TODO: HANDLE TERMINATIONS

class GameServer:
    def __init__(self,
                 use_local,
                 temp_dir_path=TEMP_DIR,
                 prompts_json_path=PROMPTS_JSON_PATH,
                 filtered_words_json_path= FILTERED_WORDS_JSON_PATH,
                 server_ip=os.getenv("SERVER_IP"),
                 server_port=os.getenv("SERVER_PORT"),
                 remove_temp=True,
                 stream_llm=True):

        # general file init
        self.temp_dir = h.init_temp_storage(temp_dir_path)
        self.remove_temp = remove_temp
        self.prompts = h.read_prompts_json(prompts_json_path)
        self.filtered_word_dicts = h.read_json(filtered_words_json_path) # dictionary of words to replace
        # file transfer setup
        self.tcps = tcp.TCPServer(server_ip, server_port)

        # init LLM handler
        self.llm = LLM(os.getenv("KEY"), stream=stream_llm)

        self.ending_prob_fact = INIT_ENDING_PROBABILISTIC_FACTOR

        self.use_local = use_local # flag if server isnt started to run a local version for debugging/testing
        self.imu_round = False     # determines whether current round will use IMU data rather than speech recognition
        print(f"LOCAL DEBUGGING SET TO: {use_local}")
        print("-----------------------------------------------")
        print("\n\n\tGame Initialization Complete\n\n")
        print("-----------------------------------------------")

    def start_server(self):
        if not self.use_local:
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

        # For IMU round, send IMU_ROUND signal first
        if self.imu_round:
            self.tcps.send_signal(Signals.IMU_ROUND)

        # Otherwise, first signal indicates the start of a streamed message
        if not self.use_local:
            self.tcps.send_signal(Signals.INIT_FT_STREAMED)
        first_message = True
        chunk_num = 0 # enumerate the chunks in each stream response
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
            if not self.use_local:
                self.convert_tts_and_send_client(chunk, chunk_num=0) # chunk num is only used for local debugging
            else:
                self.convert_tts_and_send_client(chunk, chunk_num=chunk_num)
            chunk_num+=1

        # signals the end of a file stream
        if not self.use_local:
            self.tcps.send_signal(Signals.END_FT_STREAMED)

        # add to the chat history
        msg = "".join(chunks)
        self.llm.add_chat_history(role, msg) # update the llm chat history

        return msg

    def execute_single_game_round(self, role="user", prompt=None, force_response=True):
        # force response continues rerunning until you recognize a response

        prompt_successful = self.llm.prompt_llm(role, prompt)

        llm_res = self.convert_and_send_llm_response()

        sig, client_res = self.get_client_response()

        # locks and continuously asks for a new response
        while client_res is None and force_response:
            self.convert_tts_and_send_client("Sorry, I didn't catch that could you say that again?", 0)
            sig, client_res = self.get_client_response()

        return client_res

    def convert_tts(self, audio_text):
        # convert LLM response text to bear audio file
        temp_wav_path = self.temp_dir / f"temp_{int(time.time())}.wav"
        temp_wav_path = tba.convert_text_to_bear_audio_opt(audio_text, temp_wav_path, self.temp_dir)

        return temp_wav_path

    def convert_tts_and_send_client(self, audio_text, chunk_num):
        if audio_text == "": # don't attempt to send if nothing to send
            return

        # check if we are just doing local debugging (no client)
        if not self.use_local:
            temp_wav_path = self.convert_tts(audio_text)
            self.tcps.send_file(temp_wav_path)
        else: #do not play audio if running local debugging
            #am.play_audio(temp_wav_path)
            if chunk_num == 0: # first chunk in message
                print("-----------------------------------------------")
                print(f"ChatGPT says: \n[CHUNK 0]{audio_text}")
            else:
                print(f"[CHUNK {chunk_num}] {audio_text}")

    def get_client_response(self):
        print("Waiting for client response")
        # get a client wav message and process
        if not self.use_local:
            # client should get stuff here
            client_wav_path = self.temp_dir / "client_res.wav"
            received_signal = self.tcps.receive_signal(expected_signals=[Signals.FILE_SENT,
                                                                         Signals.IMU_TURN_LEFT,
                                                                         Signals.IMU_TURN_RIGHT])
            if received_signal == Signals.FILE_SENT: # received an audio file
                client_wav_path = self.tcps.receive_file(client_wav_path)
                client_res = timeit(sp.recognize_wav)(client_wav_path)
                print(f"You said: {client_res}")

            # imu signals
            elif received_signal == Signals.IMU_TURN_LEFT:
                client_res = self.prompts["IMU_turn_left"]
            elif received_signal == Signals.IMU_TURN_RIGHT:
                client_res = self.prompts["IMU_turn_right"]
            # handling imu signals
        else: # local mode that just takes a user input for text
            received_signal = Signals.FILE_SENT
            client_res = input("--------> You respond: ")
            print("-----------------------------------------------")

        return received_signal, client_res


    def update_ending_prob_factor(self):
        if self.ending_prob_fact >= 4: # sets the highest probability of 
            self.ending_prob_fact -= 1

    def main_loop(self, initial_prompt):
        prompt = initial_prompt
        round_num = 0 # round 0 is the first round that a story decision is presented to the child
        # Variables for the game logic
        enforce_game_enders = False
        while True:
            #Determine if this situation will have a game ending choice probabilistically
            # (PROBABILISTIC_FACTOR)^(-1)% chance of a potentially game ending round
            #if round_num >= NUM_SAFE_ROUNDS and random.randint(1,1) == 1:
            if round_num == 3:
                print("----------This round will have potential game enders---------")
                self.llm.add_chat_history("system", self.prompts["next_round_random"])
                enforce_game_enders = True
            else:
                enforce_game_enders = False
            # 33% chance of IMU round
            if (not enforce_game_enders) and (random.randint(1,1) == 0 and prompt != initial_prompt):
                self.imu_round = True
                # Add chat history to affect the next LLM response
                self.llm.add_chat_history("system", self.prompts["this_round_imu"])

            self.llm.prompt_llm(prompt=prompt)
            llm_res = self.convert_and_send_llm_response()

            #TODO clean this up
            if "for playing" in llm_res:
                print("Game is over!")
                # send termination signal here
                self.tcps.send_signal(Signals.GAME_END)
                break

            self.imu_round = False

            sig, prompt = self.get_client_response()
            print("Got client response")

            # If we are in a game ending probabilistic round, handle cases when the child chooses a failure option intelligently
            # Note that we create separate LLM API calls to determine option choice and failure option. Empirically, the additional delay is negligible.
            if enforce_game_enders:

                # Ask LLM to determine which option the child chose so we have a numerical value [1, 3]
                option_check_string = llm_res + '\n\n' + prompt + '\n\n' + self.prompts["option_check"]
                selected_choice = self.llm.prompt_llm_single(prompt=option_check_string)
                int_selected_choice = extract_option_number(selected_choice)

                print("**START DEBUG INFO**")
                if int_selected_choice is None:
                    int_selected_choice = 1
                    print("Unable to parse selection option number from:\n" + selected_choice)
                else:
                    print(f"Selected option number: {int_selected_choice} from: \"{selected_choice}\"")
                print("**END DEBUG INFO**")
                

                # Ask LLM to determine which option is most likely to end in failure so we have a numerical value [1, 3]
                print("**START DEBUG INFO**")
                failure_check_string = self.prompts["which_option_fails"] + "\n\n" + llm_res
                failure_option = self.llm.prompt_llm_single(prompt=failure_check_string)
                int_failure_choice = extract_option_number(failure_option)
                if int_failure_choice is None:
                    int_failure_choice = 1
                    print("Unable to parse failure option number from:\n" + failure_option)
                else:
                    print(f"Failure option number: {int_failure_choice} from: \"{failure_option}\"")
                print("**END DEBUG INFO**")
                

                # If the child selected the game ending option
                if True:
                    print("FAILURE. Ending Game")
                    if self.use_local:
                        sys.exit()
                    else:
                        self.llm.add_chat_history("system", self.prompts["failure"])
                        self.llm.prompt_llm(prompt=prompt)
                        llm_res = self.convert_and_send_llm_response()
                        self.tcps.send_signal(Signals.GAME_END)


            if round_num >= 2:
                self.update_ending_prob_factor()

            round_num += 1

    def __del__(self):
        if self.remove_temp:
            shutil.rmtree(self.temp_dir)

def main():

    # -d option enables local debugging without a client
    # use: python game_server.py -d
    parser = argparse.ArgumentParser(description='Game server program for the choose your own adventure game.')
    parser.add_argument('-d', action='store_true', help='Enable local debugging (i.e. do not use client)')

    args = parser.parse_args()
    local_debug = args.d

    game_server = GameServer(local_debug)

    game_server.start_server()

    story_setting = game_server.init_game()

    game_server.main_loop(story_setting)

if __name__ == '__main__':
    main()
