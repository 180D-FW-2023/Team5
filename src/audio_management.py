import time
import wave
import pyaudio
import queue

from constants import *

FORMAT = pyaudio.paInt16 # data type formate

def open_audio_file(path):
    path = str(path)
    try:
        f = wave.open(path, "rb")
        print(f'{path} Opened: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    except wave.Error as e:
        print(e)
        return None

    return f

def record_audio_by_time(output_file_path, record_time=5):
    output_file_path = str(output_file_path)
    # Startup pyaudio instance
    audio = pyaudio.PyAudio()

    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    frames = []

    # Record for RECORD_SECONDS
    initial_run = True
    start = time.time()
    for i in range(0, int(RATE / CHUNK * record_time)):
        data = stream.read(CHUNK)
        if initial_run:
            initial_run = False
            print(f"\n\nSTARTED RECORDING DELAY BETWEEN START AND RECORDING: {time.time()-start}\n\n")
        frames.append(data)


    # Stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Write your new .wav file with built in Python 3 Wave module
    waveFile = wave.open(output_file_path, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

    return output_file_path

def play_audio(path):
    path = str(path)
    f = open_audio_file(path)
    if f is None:
        return False # failed to play

    audio = pyaudio.PyAudio()
    stream = audio.open(
                format = audio.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True
                )

    data = f.readframes(CHUNK)
    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = f.readframes(CHUNK)


    # cleanup stuff.
    f.close()
    stream.close()
    audio.terminate()
    return True

# TODO: Consider changing this to be separately threaded. Means the mic needs to be properly handled
# incase of current playback

def play_audio_stream(input_queue):
    # takes in a queue of file paths and continuously plays
    # None is expected as the sentinel otherwise itll just keep playing cause fuck it we ball

    initial_path = input_queue.get(timeout=10) #want this one to be blocking just so it will have something
    f = open_audio_file(initial_path)
    if f is None:
        return False # failed to play
    
    # init a stream from the first input segment
    audio = pyaudio.PyAudio()
    stream = audio.open(
                format = audio.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True
                )
    
    # play the initial segment
    data = f.readframes(CHUNK)
    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = f.readframes(CHUNK)
    f.close()

    # continuously play the rest of the input queue
    # adding a timeout just in case
    start_time = time.time()
    while True:
        path = input_queue.get(timeout=10)
        if path is None: # sentinel
            break

        f = open_audio_file(path)

        data = f.readframes(CHUNK)
        while data:
            stream.write(data)
            data = f.readframes(CHUNK)
        f.close() # close to prevent dangling fd

    # clean up
    stream.close()
    audio.terminate()
    return True


if __name__ == "__main__":
    # record_audio_by_time("out.wav")
    # play_audio("out.wav")

    # testing streaming audio
    test_queue = queue.Queue()
    test_path = r"C:\code\ece180da\final_project\test_data\test_capstone.wav"
    test_queue.put(test_path)
    test_queue.put(test_path)
    test_queue.put(test_path)
    test_queue.put(test_path)
    test_queue.put(None)

    play_audio_stream(test_queue)
