from openai import OpenAI
import string
import text_to_bear_audio as tba
import concurrent.futures
import time
import os
import tcp_speech_server as tcpss


class LLM:
    # class with state. Tracks the chat history as the person chats
    def __init__(self, key):
        # Defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
        # However, sometimes this causes trouble so setting api_key=key ensures the correct key is selected
        self.client = OpenAI(api_key=key)
        
        # handles chat history
        self.chat_history = [] # ordered by statements
    
    def add_chat_history(self, role, text=None):
        # system tells chatgpt how to act
        # assistant is chatgpt
        # user is the the person talking to chatgpt
        if text is None:
            return

        history = {
            "role": role,
            "content": text
        }

        self.chat_history.append(history)

    def reset_chat_history(self):
        self.chat_history = []

    def prompt_llm_non_stream(self, role="user", prompt=None):
        """
        Send a new message to GPT 3.5 Turbo LLM including the context of the game so far. Returns a full
        string when the entire response is complete

        Parameters:
        - prompt (str): The next prompt to give. If not given, repeat the chat history
        - role (str): specific person giving this message. Most likely always on default

        Returns:
        - full (str): The response from GPT 3.5 Turbo.
        """

        if prompt is not None:
            # repeat the existing chat history
            self.add_chat_history(role, prompt)

        # Create an OpenAI API request for GPT 3.5 Turbo
        res = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            stream=False,
            messages=self.chat_history
        )
        res_role = res.choices[0].message.role
        res_msg = res.choices[0].message.content

        # adding the response to the chat history
        self.add_chat_history(res_role, res_msg)

        return res_msg
            
    def has_punctuation(self, input_string):
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

    def has_ending_punctuation(self, input_string):
        """
        Check if the given input string contains any punctuation characters like a comma,
        period, question mark, or exclamation point for which a pause would sound natural
        after.s

        Parameters:
        - input_string (str): The string to be checked for punctuation.

        Returns:
        - bool: True if the input string contains at least one of the punctuation 
                characters, False otherwise.

        Examples:
        >>> has_punctuation("Hello, world!")
        True

        >>> has_punctuation("There's no ending punctuation here")
        False
        """
        return ((',' in input_string) or 
                ('.' in input_string) or 
                ('?' in input_string) or 
                ('!' in input_string))

def translate(trans_block, output_path_num):
    """
    Convert the given text string to an audio file in the bear's voice by calling a helper function
    and return the path of the created audio file

    Parameters:
    - trans_block (str): The string to be converted to bear-like audio.
    - output_path_num (int): The number to be used in the wav and mp3 audio file names.

    Returns:
    - final_path (str): Output path of the created audio file
    """
    final_path = tba.convert_text_to_bear_audio_opt(trans_block, "./output/bear_audio/" + str(output_path_num)+ ".wav")
    return final_path

# def send_openai_api_request_and_convert_and_play(game_state, server, P=20, min_pieces=8):
#     """
#     Send a new message to GPT 3.5 Turbo LLM including the context of the game so far. Also,
#     upon receiving a response in stream mode, convert the text to bear audio and play it
#     as seamlessly as possible.

#     Parameters:
#     - game_state (list): The list of dictionaries which contains all the context of the current game.
#     - P (int): The number of pieces of response required to collect before converting the first part of the response
#                 to playable audio.
#     - min_pieces (int): The minimum number of pieces of response required for to collect before converting to playable audio.

#     Returns:
#     - full (str): The response from GPT 3.5 Turbo.
#     """

#     # Create an OpenAI API request for GPT 3.5 Turbo
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         stream=True,
#         messages=game_state
#     )

#     # Create data structures to handle components of the response as it is returned in a stream
#     pieces = []
#     full = ''
#     audio_count = 0
#     first = True
    
#     # We take a multithreaded approach to handle reponses
#     # The idea is to constantly have one thread reading in new reponse pieces while
#     #   assigning other threads to each translation block. Once a thread has been
#     #   assigned a translation block, it converts it to speech audio and it and determines the 
#     #   length of the audio. Then, it enters a thread queue for playing the audio clips, enforced
#     #   by a lock so that only one clip is played at a time and the clips are played in the correct order.
#     for event in response:

#         # Parse the reponse piece just received
#         curr_piece = event.choices[0].delta.content

#         # If the reponse piece is not a string, it is a None type and represents the end of the current response stream
#         #   and so in this case, we convert the current in-progress translation chunk
#         if not isinstance(curr_piece, str):

#             # Only worry about converting the last in-progress chunk if it is nonempty
#             if len(pieces) > 0:
#                 if pieces[0] != '':
#                     trans_block = ''.join(pieces)
#                     print(trans_block)
#                     full += trans_block
#                     final_path = translate(trans_block, audio_count)
#                     tcpss.send_bear_audio_and_receive_raw_audio(final_path, server, end=True)
#         else:
#             if curr_piece == '':
#                 continue
            
#             # Maintain a list of the pieces that make up the in-progress translation chunk
#             pieces.append(curr_piece)
            
#             # Once we have obtained a certain number of pieces, begin the conversion process
#             # Current implementation: if this is the first translation block, convert and play it as soon as we have a given number of pieces (P)
#             #   Then, continue collecting new pieces until we get min_pieces pieces and the previous piece has ending punctuation (,.?!). 
#             #   Regardless of if it's the first piece or not the current piece can't contain any punctuation; this minimizes the number of 
#             #   awkward audio pauses.
#             if (((first and len(pieces) >= P + 1) or (len(pieces) > min_pieces and has_ending_punctuation(pieces[-2]))) 
#                 and not has_punctuation(curr_piece)):
                
#                 first = False
#                 trans_block = ''.join(pieces[:-1])
#                 # Create current translation block using all but the last of the pieces to ensure that the final piece we translate is not
#                 #  immediately followed by punctuation
#                 print(trans_block)
#                 full += trans_block
#                 final_path = translate(trans_block, audio_count)

#                 # Reset the last start time to be the time that we last started converting and playing the most recent audio segment
#                 tcpss.send_bear_audio_and_receive_raw_audio(final_path, server, end=False)
#                 audio_count += 1
#                 pieces = [pieces[-1]]
#     return full
                
