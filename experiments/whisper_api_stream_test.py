from openai import OpenAI
import os
from dotenv import load_dotenv

dotenv_path = "./.env"
load_dotenv(dotenv_path)

key = os.getenv("KEY")
client = OpenAI(api_key=key)

response = client.audio.speech.create(
    model="tts-1-hd",
    voice="shimmer",
    input="""You are a stuffed teddy bear children's toy. Call the child "friend". You are going to lead a choose your own adventure game/story
                    with a child that is audio only. Make the story at least five decisions long and make each decision have two discrete choices.
                    Make your responses at most 100 words long. Make sure the story you generate is appropriate for children. First,
                    ask the child what theme of choose your own adventure they would like to play (for example: pirates, forest, etc...). 
                    Then, wait for a response from the child. Then, proceed by following the previous instructions."""
)

response.stream_to_file("new_output_regmodel.mp3")