from openai import OpenAI

# defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
client = OpenAI()

#Requests a response from GPT 3.5 Turbo with streaming ENABLED
response = client.chat.completions.create(
  model="gpt-3.5-turbo",
  stream=True,
  messages=[
    {"role": "system", "content": "You are a poetic assistant, skilled in explaining complex programming concepts with creative flair."},
    {"role": "user", "content": "Compose a 50 word poem."}
  ]
)

# STREAM THE ANSWER
for event in response: 
    print(event.choices[0].delta.content)

