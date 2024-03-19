
# Code Information for experiments directory

The experiments folder contains various testing files:

```end_to_end_speech_test.py``` - 
Tests sound card drivers.

```local_speech_test.py``` -
Tests speech processing on local systems. 

```stream_test.py``` -
Tests streaming feature from the API.

```tcp_speech_client_test.py``` -
Tests speech file detection on the client's end.

```tcp_speech_server_test.py``` -
Tests speech file detection on the server's end.

```whisper_api_stream_test.py```-
Tests initial call to the API.

These files do not contain much code as they are simply testing other functions and files we have written, and they do not have any bugs that we are aware of. That being said, we could definitely improve experiments by standardizing our testing methods and combining them into a unit test. There are also other tests we could add, for example, testing client + server setup without having to manually start each, as well as testing the Raspberry Pi boot process.
