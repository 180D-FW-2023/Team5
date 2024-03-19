
# Code Information for src directory

The main body of our code is located in the src folder. Below is a brief description of each file:

```constants.py``` - This file holds global constants for our main routine. The most essential values are the timing between recording user inputs and the probability of game-ending prompts. 

```game_client.py``` -
  Driver code to run the game on the Raspberry Pi. We used some code from the threading, pyaudio, and subprocess libraries' official documentation. The main steps in the execution of this file are:
  
1) Attempt to connect to the server
2) Initialize client game variables and modes (i.e. using IMU, pyaudio vs subprocess)
3) Receive signal from the server
4) Collect input from the user depending on the signal received (i.e. record with microphone using multithreading if normal round, collect IMU data if IMU round, etc.)
5) Send file or data to server
6) Repeat steps 3-5 until game ends or connection closes.

```game_server.py``` -
   Driver code for the game to run on the computer, including calls to the LLM. We followed ChatGPT's API documentation.

1) Establish TCP connection with the client
2) Initialize ChatGPT with our API key
3) Prompt ChatGPT to ask the player for their name and send the result to the client
4) Tell ChatGPT the player's name and create a prompt to ask the player for a theme and send the result to the client
5) Add the client response to the chat history and determine the next round according to the game logic.
6) Craft a prompt for ChatGPT and stream the response to the client
7) Receive a signal or data from the client as their response.
8) Repeat steps 5-7 until the game ends or connection closes.

```helper.py``` -
  Includes testing protocols and assists in file loading.

- timeit(): takes a function as input, runs it and outputs the time it took.
- init_temp_storage(): initialize temporary directory for temporary audio files
- read_file_as_str(): read a file's data as a string
- read_json(): read the data in a json file (used for filtered_words.json)
- read_prompts_json(): read the data from prompts.json
- get_first_number(): get the first number in a string. Used by server to parse LLM output for game logic.

```llm_handler.py``` -
  A file that calls OpenAI and relays prompts to and from ChatGPT. We followed ChatGPT's API documentation.

- init(): Initialize the ChatGPT API and create a thread for llm_producer (see below)
- add_chat_history(): add text to the chat history as "system", "assistant", or "user"
- get_last_message(): get the last message in the chat history
- reset_chat_history(): clear the chat history
- prompt_llm_single(): send a new message to GPT 3.5 Turbo LLM without the context of the game so far. Intended for quick responses so result isn't streamed.
- prompt_llm(): send a new message to GPT 3.5 Turbo LLM including the context of the game so far. Returns a full string when the entire response is complete
- save_chat_history(): dump the chat history into a json object
- load_chat_history(): load chat history from a json object
- has_chars(): returns true if input string has any of the provided characters; used to check if streaming response has any delimiters
- split_delimiters(): splits a string by multiple delimiters
- replace_words(): remove filtered words and replace with replacement words
- llm_producer(): repeatedly checks input queue for ChatGPT API, takes response and splits based on delimiters, then places chunks in an output queue for server to read from


```play_and_record_audio.py``` -
  Controls our system's microphone and speakers. We followed pyaudio and subprocess documentation.

- open_audio_file(): opens a wav file and plays it
- record_audio functions: various functions to record audio using either pyaudio or subprocess
- play_audio functions: various functions to play audio file or stream using either pyaudio or subprocess

```signals.py``` -
  Enumeration of critical signals including sending files and ending the game.

```speech_to_text.py``` -
  Translates user audio to text using vosk and stores it in a JSON file. This file is then processed by the LLM. We used documentation from vosk, speech_recognition, subprocess, and sounddevice.

  - recognize_speech_from_mic(): uses Google's Speech-to-Text API to record audio until the user stops talking and converts the recording to a string
  - gather_speech_data(): repeatedly calls recognize_speech_from_mic() until valid result is achieved
  - recognize_wav(): run Speech-to-Text on an already existing audio file
  - recognize_wav_vosk(): run Speech-to-Text using Vosk's local model; not currently used in our final project

  ```tcp_file_transfer.py``` -
  TCP server and client structure/protocol. Contains functions for sending and receiving signals, strings, files, and file streams, as well as functions for establishing a TCP connection between client and server. We followed socket and TCP documentation for this file.

  ```text_to_speech.py``` -
  Converts text-file from the API to speech in the toy's voice. We used code from the official documentation for Google Text-to-Speech, ffmpeg, pydub, numpy, wave, and os.

  - play_wav(): runs the "aplay" command in the background to play a wav file
  - split_into_two_pieces(): split a long string with no punctuation into two pieces based on words that sound natural with a pause before them
  - text_str_valid(): determine if a string is valid for converting to speech
  - convert_text_to_bear_audio(): creates a playful voice wav file and plays it
  - convert_text_to_bear_audio_opt(): does the same thing as above, but uses ffmpeg to be more efficient

  ```rpi_boot.py``` -
  Initiates Wi-Fi and the client code on the Raspberry Pi.

  - check_internet_connection(): ping an IP to check the Internet connection on the Raspberry Pi.
  - configure_wifi(): modify wpa_supplicant.conf file to configure wifi, run commands to refresh configs, attempt to connect to wifi, and begin the game if successful.

The main bug we've encountered is in speech_to_text.py, where occasionally the API call takes an unusually long amount of time to process speech. Some things to work on would be to experiment with different speech recognition and LLM APIs. There is also plenty of additional complexities that could be integrated into the game logic in game_server.py.