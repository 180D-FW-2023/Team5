import speech_processing as sp

if __name__ == '__main__':
    speech = sp.gather_speech_data()
    print("you said: " + speech)