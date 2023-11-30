import random
import time
import speech_recognition as sr

# Function for speech recognition from a WAV file
def recognize_wav(file_path):

    # Initialize recognizer
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        # Using Google Web Speech API
        text = recognizer.recognize_google(audio_data)
        print("Text from WAV file:", text)
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error with the request to Google Speech Recognition service; {e}")

# Function for speech recognition from a WAV file
def recognize_wav(file_path):

    # Initialize recognizer
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)

    try:
        # Using Google Web Speech API
        text = recognizer.recognize_google(audio_data)
        print("Text from WAV file:", text)
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error with the request to Google Speech Recognition service; {e}")


    