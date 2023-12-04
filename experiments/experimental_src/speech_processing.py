import random
import time
import speech_recognition as sr

# Converts the recorded audio to text
def recognize_speech_from_mic(recognizer, microphone):

    if not isinstance(recognizer, sr.Recognizer):
        raise TypeError("`recognizer` must be `Recognizer` instance")

    if not isinstance(microphone, sr.Microphone):
        raise TypeError("`microphone` must be `Microphone` instance")

    with microphone as source:

        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        response = {
            "success": True,
            "error": None,
            "transcription": None
        }

        try:
            response["transcription"] = recognizer.recognize_google(audio)
        except sr.RequestError:
            response["success"] = False
            response["error"] = "API unavailable"
        except sr.UnknownValueError:
            response["error"] = "Unable to recognize speech"

        return response

# Top level function for recording audio and translating to text
def gather_speech_data():
    PROMPT_LIMIT = 5
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        for j in range(PROMPT_LIMIT):
            print('Speak!')
            guess = recognize_speech_from_mic(recognizer, microphone)

            if guess["transcription"]:
                break
            if not guess["success"]:
                break

            print("I didn't catch that. What did you say?\n")

        if guess["error"]:
            print("ERROR: {}".format(guess["error"]))
            break

        #print("You said: {}".format(guess["transcription"]))

        return guess["transcription"]

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
       
        return text
    except sr.UnknownValueError:
        print("Could not understand audio.")
    except sr.RequestError as e:
        print(f"Error with the request to Google Speech Recognition service; {e}")
