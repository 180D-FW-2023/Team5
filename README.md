
# Interactive Adventure Game Toy

Teddy bear with IOT-enabled speaker to play interactive choose-your-own-adventure games
using ChatGPT as a backend

Use python game_server.py -d to enable local debugging

The main body of our code is located in the src folder. Below is a brief description of each file:

constants.py-
  This file holds global constants for our main routine. The most essential values are the timing between recording user inputs and the probability of game-ending prompts. 

game_client.py
  Driver code to run the game on the Raspberry Pi. 

game_server.py
  Driver code for the game to run on the computer, including calls to the LLM.

helper.py
  Includes testing protocols and assists in file loading.

llm_handler.py
  A file that calls OpenAI and relays prompts to and from ChatGPT

play_and_record_audio.py
  

