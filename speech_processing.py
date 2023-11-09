import random
import time
import speech_recognition as sr

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


if __name__ == "__main__":
    gather_speech_data()
    