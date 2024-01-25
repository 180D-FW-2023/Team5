#Sets the record time (in seconds) when the RPI listens to the child
RECORD_TIME = 2.5

# sets the time in seconds to wait between playing and recording
AUDIO_SWITCH_DELAY = 3
RECEIVED_FILE_PATH = "temp.wav"
TEMP_DIR = "temp"
PROMPTS_JSON_PATH = "data/prompts.json"
FILTERED_WORDS_JSON_PATH = "data/filtered_words.json"
DOTENV_PATH = ".env" # check in src

# llm params
PROMPT_DELIMITERS =  ["?", "!", ".", ";"]

# recording settings
CHANNELS = 2 # Adjust to your number of channels
RATE = 44100 # Sample Rate
CHUNK = 1024 # Block Size

# game logic
ENDING_STRING = "for playing" # chat gpt phrase that signals end
PROBABILISTIC_FACTOR = 1 #Sets the probability that a given situation will have actions that result in probabilistic game ending
# ^ This is the deminator in the probability where the numerator is always 1. i.e. setting this to 5 results in a 20% probability
FAILURE_FACTOR = 1 #Same idea as previous constant except this controls the probability of failure itself