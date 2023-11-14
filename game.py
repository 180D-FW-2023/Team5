import speech_processing as sp
import text_to_bear_audio as tba
import stream_test as st

def main():
    speech = sp.gather_speech_data()
    print("you said: " + speech)

    st.make_api_call(speech)

    tba.convert_text_to_bear_audio(speech)


if __name__ == '__main__':
    main()