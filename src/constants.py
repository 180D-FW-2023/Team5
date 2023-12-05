#Sets the record time (in seconds) when the RPI listens to the child
RECORD_TIME = 10
RECEIVED_FILE_PATH = "temp.wav"
TEMP_DIR = "temp"
PROMPTS_JSON_PATH = "data/prompts.json"
DOTENV_PATH = ".env" # check in src

RECORD_TIME = 10 # seconds to record childs response

# recording settings
CHANNELS = 2 # Adjust to your number of channels
RATE = 44100 # Sample Rate
CHUNK = 1024 # Block Size

# game logic
ENDING_STRING = "for playing" # chat gpt phrase that signals end
