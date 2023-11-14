
# from openai import OpenAI
# import time
# import os

# client = OpenAI()

# startime = time.time()

# ### STREAM CHATGPT API RESPONSES
# delay_time = 0.01 #  faster
# max_response_length = 200
# answer = ''
# # ASK QUESTION
# prompt = input("Ask a question: ")
# start_time = time.time()

# completion = client.chat.completions.create(
#   model="gpt-3.5-turbo",
#   messages=[
#     {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
#     {"role": "user", "content": "Compose a poem that explains the concept of recursion in programming."}
#   ]
# )

# print(completion.choices[0].message)

from openai import OpenAI
import time

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
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a 10 word poem."}
  ]
)

#STREAM THE ANSWER
for event in response: 
    print(event.choices[0].delta.content)
