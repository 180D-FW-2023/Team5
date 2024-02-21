
# Interactive Adventure Game Toy

Teddy bear with IOT-enabled speaker to play interactive choose-your-own-adventure games
using ChatGPT as a backend

Use python game_server.py -d to enable local debugging

The main body of our code is located in the src folder. Below is a brief description of each file:

```constants.py``` - This file holds global constants for our main routine. The most essential values are the timing between recording user inputs and the probability of game-ending prompts. 

```game_client.py``` -
  Driver code to run the game on the Raspberry Pi. 

```game_server.py``` -
   Driver code for the game to run on the computer, including calls to the LLM.

```helper.py``` -
  Includes testing protocols and assists in file loading.

```llm_handler.py``` -
  A file that calls OpenAI and relays prompts to and from ChatGPT.

```play_and_record_audio.py``` -
  Controls our system's microphone and speakers. 

```signals.py``` -
  Enumeration of critical signals including sending files and ending the game.

```speech_to_text.py``` -
  Translates user audio to text using vosk and stores it in a JSON file. This file is then processed by the LLM.

  ```tcp_file_transfer.py``` -
  TCP server and client structure/protocol. 

  ```text_to_speech.py``` -
  Converts text-file from the API to speech in the toy's voice.

  ```rpi_boot.py``` -
  Initiates Wi-Fi and the client code on the Raspberry Pi.

The data folder contains code for the configuration of our game:

```filtered_words.json``` -
Simplifies possible outputs from the API to vocabulary appropriate for a child

```prompts.json``` -
Converts user inputs/choices to appropriate responses by sending designated prompts to the API based on previous actions. 

The experiments folder contains various testing files:

```end_to_end_speech_test.py``` - 
Tests sound card drivers.

```local_speech_test.py``` -
Tests speech processing on local systems. 

```stream_test.py``` -
Tests streaming feature from the API.

```tcp_speech_client_test.py``` -
Tests speech file detection on the client's end.

```tcp_speech_server_test.py``` -
Tests speech file detection on the server's end.

```whisper_api_stream_test.py```-
Tests initial call to the API.


The IMU folder contains the software backend for the implementation of kinematic controls, though we still have not been able to integrate the hardware.

The necessary packages for our system are located in ```requirements-client.txt``` and ```requirements-server.txt```.


  
  



  


  
  

