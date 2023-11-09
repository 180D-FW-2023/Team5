import speech_processing as sp
import text_to_bear_audio as tba

def main():
    speech = sp.gather_speech_data()
    print("you said: " + speech)

    # TODO: Make API call

    tba.convert_text_to_bear_audio(speech)


if __name__ == '__main__':
    main()