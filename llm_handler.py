from openai import OpenAI
import string
import text_to_bear_audio as tba
import concurrent.futures
import time
import os
from dotenv import load_dotenv

# Maunally load environment variables from the .env file
# Set KEY=<your_api_key> in the .env file for this to work
dotenv_path = "./.env"
load_dotenv(dotenv_path)
key = os.getenv("KEY")

# Defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
# However, sometimes this causes trouble so setting api_key=key ensures the correct key is selected
client = OpenAI(api_key=key)

def create_game_state_addition(role, prompt):
    """
    Convert a given role and string to a valid game state addition.

    Parameters:
    - role (str): The role of the entity adding to the game state, either 'system' or 'user'.
    - prompt (str): The text string to add to the game state.

    Returns:
    - dict: Valid dictionary that represents an addition to the game state.
    """
    return {"role": role, "content": prompt}

def has_punctuation(input_string):
    """
    Check if the given input string contains any punctuation characters.

    Parameters:
    - input_string (str): The string to be checked for punctuation.

    Returns:
    - bool: True if the input string contains at least one punctuation character,
            False otherwise.

    Examples:
    >>> has_punctuation("Hello, world!")
    True

    >>> has_punctuation("No punctuation here")
    False
    """
    return any(char in string.punctuation for char in input_string)

def translate_and_get_duration(trans_block, output_path):
    """
    Convert the given text string to an audio file in the bear's voice by calling a helper function
    and return the length of the created audio file and path of the created audio file

    Parameters:
    - trans_block (str): The string to be converted to bear-like audio.

    Returns:
    - duration (int): Time in seconds of the created audio file.
    - final_path (str): Output path of the created audio file
    """
    duration, final_path = tba.convert_text_to_bear_audio(trans_block, output_path)
    return duration, final_path

def send_openai_api_request(game_state, P=20, TTS_time=2):
    """
    Send a new message to GPT 3.5 Turbo LLM including the context of the game so far. Also,
    upon receiving a response in stream mode, convert the text to bear audio and play it
    as seamlessly as possible.

    Parameters:
    - game_state (list): The list of dictionaries which contains all the context of the current game.
    - P (int): The number of pieces of response required to collect before converting the first part of the response
                to playable audio.
    - TTS_time (int): An empirically selected time in seconds required to (roughly) convert a given text string to speech audio.

    Returns:
    - full (str): The response from GPT 3.5 Turbo.
    """

    # Create an OpenAI API request for GPT 3.5 Turbo
    begin_time = time.time()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        stream=True,
        messages=game_state
    )

    # Create data structures to handle components of the response as it is returned in a stream
    pieces = []
    full = ''
    audio_count = 0
    required_time = 1e10
    first = True
    last_start_time = 0
    
    # We take a multithreaded approach to handle reponses
    # The idea is to constantly have one thread reading in new reponse pieces while
    #   assigning other threads to each translation block. Once a thread has been
    #   assigned a translation block, it converts it to speech audio and it and determines the 
    #   length of the audio. Then, it enters a thread queue for playing the audio clips, enforced
    #   by a lock so that only one clip is played at a time and the clips are played in the correct order.
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for event in response:

            # Parse the reponse piece just received
            curr_piece = event.choices[0].delta.content

            # If the reponse piece is not a string, it is a None type and represents the end of the current response stream
            #   and so in this case, we convert the current in-progress translation chunk
            if not isinstance(curr_piece, str):

                # Only worry about converting the last in-progress chunk if it is nonempty
                if len(pieces) > 0:
                    trans_block = ''.join(pieces)
                    full += trans_block
                    required_time, final_path = translate_and_get_duration(trans_block, audio_count)
                    executor.submit(tba.play_wav, final_path)
            else:
                if curr_piece == '':
                    continue
                
                # Maintain a list of the pieces that make up the in-progress translation chunk
                pieces.append(curr_piece)
                
                # Once we have obtained a certain number of pieces or run out of time to collect pieces, begin the conversion process
                # Current implementation: if this is the first translation block, convert and play it as soon as we have a given number of pieces (P)
                #   Then, continue collecting new pieces until we get close to the time that the current audio clip will be ending, at which point
                #   we convert the next in-progress chunk. Note two things: "too close" to the previous audio clip finishing is based on the
                #   TTS_time paramter, which is an estimate of how long the conversion process will take AND we will only convert the current
                #   chunk if the last chunk IS NOT IMMEDIATELY FOLLOWED BY PUNCTUATION. This minimizes the number of awkward audio pauses.
                if ((first and len(pieces) >= P + 1) or (time.time() - last_start_time > required_time - TTS_time)) and not has_punctuation(curr_piece):
                    first = False
                    # Create current translation block using all but the last of the pieces to ensure that the final piece we translate is not
                    #  immediately followed by punctuation
                    trans_block = ''.join(pieces[:-1])
                    print(trans_block)
                    full += trans_block
                    required_time, final_path = translate_and_get_duration(trans_block, audio_count)

                    # Reset the last start time to be the time that we last started converting and playing the most recent audio segment
                    last_start_time = time.time()
                    executor.submit(tba.play_wav, final_path)
                    audio_count += 1
                    pieces = [pieces[-1]]
    return full
                
