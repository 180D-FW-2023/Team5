import string
import queue
import threading

from openai import OpenAI

from constants import *
import text_to_speech as tba

class LLM:
    # class with state. Tracks the chat history as the person chats
    def __init__(self, key, stream=True):
        # Defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
        # However, sometimes this causes trouble so setting api_key=key ensures the correct key is selected
        self.client = OpenAI(api_key=key)

        # handles chat history
        self.chat_history = [] # ordered by statements

        # used to communicate across threads. Single thread as we expect a single producer/consumer at all times.
        self.prompt_queue = queue.Queue(maxsize=3) # a queue to send prompts for processing to the llm thread. None signals the end of the process

        # expected to clear every new prompt so we dont need to indicate the start
        self.response_queue = queue.Queue(maxsize=20) # a queue of all the sentences received from llm. None means the previous message is done. 

        self.stream = stream

        # initialize a separate thread for all the thread stuff for multithreading
        self.producer_thread = threading.Thread(target=llm_producer, 
                                                args=(self.prompt_queue, 
                                                      self.response_queue, 
                                                      self.client, 
                                                      self.stream), 
                                                daemon=True)
        self.producer_thread.start()

    def __del__(self):
        self.producer_thread.join()

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

    def get_last_message(self, role=None):
        if role is None:
            return self.chat_history[-1]
        else:
            for chat_log in self.chat_history[::-1]:
                if chat_log["role"] == role:
                    return chat_log["content"]

    def reset_chat_history(self):
        self.chat_history = []

    def prompt_llm(self, role="user", prompt=""):
        """
        Send a new message to GPT 3.5 Turbo LLM including the context of the game so far. Returns a full
        string when the entire response is complete

        Parameters:
        - prompt (str): The next prompt to give. If not given, repeat the chat history
        - role (str): specific person giving this message. Most likely always on default

        Returns:
        - full (str): The response from GPT 3.5 Turbo.
        """
        if prompt is None:
            print("NO PROMPT GIVEN")
            return False

        if prompt != "":
            # repeat the existing chat history
            self.add_chat_history(role, prompt)
        else:
            print("EMPTY PROMPT GIVEN. RERUNNING THE PREVIOUS CHAT HISTORY")
        self.prompt_queue.put(self.chat_history)

        return True

def has_chars(input_string, chars):
    # returns true if the string has any of the given chars
    return any(char in chars for char in input_string)

def split_delimiters(input_string, delimiters):
    # splits a string by multiple delimiters
    for delimiter in delimiters:
        input_string = input_string.replace(delimiter, f"{delimiter}**&**")

    return input_string.split("**&**")

def llm_producer(input_queue, output_queue, client, stream=True, n_tokens=2):
    print(f"LLM STREAM STATUS: {stream}")
    # intended for separate thread
    # n tokens is number of separated tokens to push with each chunk
    while True:
        # block indefinitely since its in a while loop
        chat_history = input_queue.get()
        if chat_history is None:
            print("LLM PRODUCER THREAD CLOSED. ")
            break

        res = client.chat.completions.create(
            model="gpt-3.5-turbo",
            stream=stream,
            messages=chat_history
        )

        if not stream:
            res_role = res.choices[0].message.role
            res_msg = res.choices[0].message.content

            output_queue.put((res_role, res_msg))
        else:
            # streamed setup
            curr_role = None
            chunks = []
            to_push = []

            for chunk in res:
                if chunk.choices[0].delta.content is None: # message is probably done or buffering
                    continue
                chunk_role = chunk.choices[0].delta.role
                curr_role = chunk_role if chunk_role is not None else curr_role # only the first chunk of the message has a role
                chunk_msg = chunk.choices[0].delta.content

                if has_chars(chunk_msg, PROMPT_DELIMITERS): # means a sentence has passed
                    split_chunk_msg = split_delimiters(chunk_msg, PROMPT_DELIMITERS)
                    # combine the last part of the first message and add to the queue
                    chunks.append(split_chunk_msg[0])
                    to_push.append("".join(chunks))

                    if len(to_push) >= n_tokens:
                        output_queue.put((curr_role, "".join(to_push)))
                        to_push = [] # reset

                    chunks = ["".join(split_chunk_msg[1:])] # add the rest of the message into the chunk queue
                    # TODO: COULD HAVE BEEN MULTIPLE SENTENCES IN ONE CHUNK
                else:
                    chunks.append(chunk_msg)
            
            if len(to_push) != 0: # clear the to push buffer
                output_queue.put((curr_role, "".join(to_push)))

            if len(chunks) != 0:
                output_queue.put((curr_role, "".join(chunks))) # put the rest of the chunks usually empty but jic

        
        # sends a signal to indicate the end of a prompt response
        output_queue.put(None)


# used for testing
if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(DOTENV_PATH)
    llm = LLM(os.getenv("KEY"))
    llm.prompt_llm(prompt="talk to me")
    llm.prompt_llm(prompt="talk to me more")
