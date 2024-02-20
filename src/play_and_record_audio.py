import time
import wave
import pyaudio
import queue
import threading
import os
import subprocess
import signal

from constants import *

global audio_lock
audio_lock = threading.Lock()

FORMAT = pyaudio.paInt16 # data type formate

#global audio
#print("Creating pyaudio instance")
# note: this takes a minute to initialize but since pyaudio doesn't like opening and closing multiple instances of pyaudio, we have to make it global
#audio = pyaudio.PyAudio()
#print("Finished creating pyaudio instance")

def open_audio_file(path):
    path = str(path)
    try:
        f = wave.open(path, "rb")
        print(f'{path} Opened: {f.getnchannels()} channels, {f.getframerate()} sampling rate\n')
    except wave.Error as e:
        print(e)
        return None

    return f



def record_audio_by_time_subprocess(output_file_path, record_time=RECORD_TIME):
    global audio_lock

    output_file_path = str(output_file_path)

    with audio_lock:
        print("Got the lock")
        #cmd = "arecord -D hw:3,0 -f S16_LE -c2 -r " + str(RATE) + " " + output_file_path
        cmd = ["arecord", "-f", "dat", "-D", "hw:3,0", output_file_path]
        try:
            # Run the command in the background
            process = subprocess.Popen(cmd)
            time.sleep(record_time)
            print(str(process.pid))
            #os.killpg(process.pid, signal.SIGTERM)
            #process.wait()
            process.kill()
            #process.wait()
        except subprocess.CalledProcessError as e:
            if "Device or resource busy" in str(e):
                print("Error: Device or resource busy. Another application may be using the soundcard.")
            else:
                print(f"An error occurred: {e}")
    print("finished recording")
    return output_file_path

def record_audio_by_time_non_subprocess(output_file_path, record_time=RECORD_TIME):
    global audio_lock
    global audio

    output_file_path = str(output_file_path)
    # Startup pyaudio instance
    with audio_lock:
        print("\nWe have the lock\n")
        """
        try:
            audio = pyaudio.PyAudio()
        except Exception as e:
            print(f"Exception {e}")
        """
        print("SUCCESS\n")

        #start Recording
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        frames = []
        print("no seg fault")
        # Record for RECORD_SECONDS
        initial_run = True
        start = time.time()
        for i in range(0, int(RATE / CHUNK * record_time)):
            print("about to listen to next chunk")
            data = stream.read(CHUNK)
            print("finished listening to next chunk")
            if initial_run:
                initial_run = False
                print(f"\n\nSTARTED RECORDING DELAY BETWEEN START AND RECORDING: {time.time()-start}\n\n")
            frames.append(data)


        # Stop Recording
        stream.stop_stream()
        stream.close()
        #audio.terminate()

        # Write your new .wav file with built in Python 3 Wave module
        waveFile = wave.open(output_file_path, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

    return output_file_path

def record_audio_by_time(output_file_path, record_time=RECORD_TIME, subprocess_mode=True):
    if subprocess_mode:
        return record_audio_by_time_subprocess(output_file_path, record_time=record_time)
    else:
        return record_audio_by_time_non_subprocess(output_file_path, record_time=record_time)

def play_audio_with_lock(path):
    cmd = ["aplay", "-D", "hw:3,0", "-f", "S16_LE", "-c2", path]
    # Run the command in the background
    process = subprocess.Popen(cmd)
    process.wait()

def play_audio_subprocess(path):
    global audio_lock

    path = str(path)

    with audio_lock:
        print("Got the lock to play")
        play_audio_with_lock(path)

    print("Done playing audio")
    return True

def play_audio_non_subprocess(path):
    global audio_lock
    global audio

    path = str(path)
    f = open_audio_file(path)
    if f is None:
        return False # failed to play

    with audio_lock:
        print("play audio thread acquired lock")
        stream = audio.open(
                    format = audio.get_format_from_width(f.getsampwidth()),
                    channels = f.getnchannels(),
                    rate = f.getframerate(),
                    output = True )

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
        print("play audio thread releasing audio lock")
    return True

def play_audio(path, subprocess_mode=True):
    if subprocess_mode:
        return play_audio_subprocess(path)
    else:
        return play_audio_non_subprocess(path)


def play_audio_stream_subprocess(input_queue):
    print("Entering play audio stream function")
    # takes in a queue of file paths and continuously plays
    # None is expected as the sentinel otherwise itll just keep playing cause fuck it we ball

    global audio_lock

    print("Beginning to wait for input queue")
    initial_path = input_queue.get(timeout=10) #want this one to be blocking just so it will have something

    # init a stream from the first input segment
    with audio_lock:
        print("play audio thread has lock")
        play_audio_with_lock(initial_path)

        # continuously play the rest of the input queue
        # adding a timeout just in case
        start_time = time.time()
        while True:
            path = input_queue.get(timeout=10)
            if path is None: # sentinel
                break

            play_audio_with_lock(path)

        print("Audio played successfully")
        print("play audio thread releasing lock")
    return True

def play_audio_stream_non_subprocess(input_queue):
    print("Entering play audio stream function")
    # takes in a queue of file paths and continuously plays
    # None is expected as the sentinel otherwise itll just keep playing cause fuck it we ball

    global audio_lock
    global audio

    print("Beginning to wait for input queue")
    initial_path = input_queue.get(timeout=10) #want this one to be blocking just so it will have something
    f = open_audio_file(initial_path)
    if f is None:
        return False # failed to play

    # init a stream from the first input segment
    with audio_lock:
        print("play audio thread has lock")
        #audio = pyaudio.PyAudio()
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
        #audio.terminate()
        print("Audio played successfully")
        print("play audio thread releasing lock")
    return True

def play_audio_stream(input_queue, subprocess_mode=True):
    if subprocess_mode:
        return play_audio_stream_subprocess(input_queue)
    else:
        return play_audio_stream_non_subprocess(input_queue)

if __name__ == "__main__":
    record_audio_by_time("out.wav")
    play_audio("out.wav")

    ## testing streaming audio
    #test_queue = queue.Queue()
    #test_path = r"C:\code\ece180da\final_project\test_data\test_capstone.wav"
    #test_queue.put(test_path)
    #test_queue.put(test_path)
    #test_queue.put(test_path)
    #test_queue.put(test_path)
    #test_queue.put(None)

    #play_audio_stream(test_queue)
