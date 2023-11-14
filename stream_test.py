
from openai import OpenAI
import time

def make_api_call(user_prompt):
    #defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
    client = OpenAI()

    delay_time = 0.01 #  faster
    max_response_length = 200
    answer = ''
    #ASK QUESTION
    start_time = time.time()

    response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    stream=True,
    messages=[
        {"role": "system", "content": "You are the master of a choose your own adventure game where the player is lost in a forest. This is what he says:"},
        {"role": "user", "content": user_prompt + "Compose a response in less than 50 words"}
    ]
    )

    #STREAM THE ANSWER
    for event in response: 
        print(event.choices[0].delta.content)

if __name__ == '__main__':

    make_api_call("what's the capital of djibouti?")
