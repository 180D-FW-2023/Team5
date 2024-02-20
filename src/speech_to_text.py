import speech_recognition as sr
import vosk
import wave
import os
import json
import subprocess

SAMPLE_RATE = 16000

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


def recognize_wav_vosk(file_path):
    # Initialize Vosk
    vosk.SetLogLevel(-1)
    model_path = r'C:\Users\niklb\Downloads\vosk-model-small-en-us-0.15\vosk-model-small-en-us-0.15'
    if not os.path.exists(model_path):
        print(f"Model not found: {model_path}")
        return -1

    model = vosk.Model(model_path)

    with wave.open(file_path, "wb") as wf:
        wf.setnchannels(1)

    # Load an audio file
    wf = wave.open(file_path, "rb")

    # if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
    #     print("Audio file must be WAV format mono PCM.")
    #     return -1

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    # recognizer.SetWords(True)
    # recognizer.SetPartialWords(True)

    speech = ""

    with subprocess.Popen(["ffmpeg", "-loglevel", "quiet", "-i",
                            file_path, "-ar", str(SAMPLE_RATE) , "-ac", "1", "-f", "s16le", "-"],
                            stdout=subprocess.PIPE) as process:
        # Process the audio
        while True:
            data = process.stdout.read(4000)
            if len(data) == 0:
                break
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                json_result = json.loads(result)["text"]
                #print(json_result)
                speech += json_result.strip()

    result = recognizer.FinalResult()
    json_result = json.loads(result)["text"]
    #print(json_result)
    speech += json_result.strip()
    return speech

    