from openai import OpenAI
import string
import text_to_bear_audio as tba
import concurrent.futures
import time
import pygame

# defaults to getting the key using os.environ.get("OPENAI_API_KEY") in .env file
client = OpenAI()
pygame.init()
pygame.mixer.init()

def has_punctuation(input_string):
    return any(char in string.punctuation for char in input_string)

def translate_and_get_duration(trans_block, output_path):
    print('-----------')
    print(trans_block)
    print('-----------')
    duration, final_path = tba.convert_text_to_bear_audio(trans_block, output_path)
    return duration, final_path

def send_api_request(prompt, P=20, translation_time=2):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        stream=True,
        messages=[
            {"role": "system", "content": "You are a child's favorite teddy bear. Always respond with exactly 100 words."},
            {"role": "user", "content": prompt}
        ]
    )

    pieces = []
    full = ''
    audio_count = 0
    required_time = 1e10
    first = True
    last_start_time = 0
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for event in response:
            curr_piece = event.choices[0].delta.content
            print(curr_piece)
            if not isinstance(curr_piece, str):
                if len(pieces) > 0:
                    trans_block = ''.join(pieces)
                    required_time, final_path = translate_and_get_duration(trans_block, audio_count)
                    executor.submit(tba.play_wav, final_path)
            else:
                if curr_piece == '':
                    continue
                
                pieces.append(curr_piece)
                
                if (first and len(pieces) >= P + 1) or (time.time() - last_start_time > required_time + 1 - translation_time) and not has_punctuation(curr_piece):
                    first = False
                    trans_block = ''.join(pieces[:-1])
                    required_time, final_path = translate_and_get_duration(trans_block, audio_count)
                    print(required_time)
                    #time.sleep(2)
                    last_start_time = time.time()
                    executor.submit(tba.play_wav, final_path)
                    audio_count += 1
                    pieces = [pieces[-1]]
                    

    print(full)

if __name__ == '__main__':
    input_text = '''
        I like to eat pizza, do you?
    '''
    send_api_request(input_text)
