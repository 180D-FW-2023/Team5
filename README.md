
# Interactive Adventure Game Toy

Teddy bear with IOT-enabled speaker to play interactive choose-your-own-adventure games using ChatGPT as a backend.

# Installation

## Server Setup

Our project requires the use of an external laptop to be used as a server to perform all computations for the RPI. All information on setup is as follows.

This system requires the use of FFmpeg. Install the full version [here](https://ffmpeg.org/download.html).

Run ```pip install -r requirements-server.txt``` to install all necessary packages on the local server.

Get your OpenAI key (more information found [here](https://platform.openai.com/api-keys) and create a ```.env``` file in the root directory of the repo with the following:
```
KEY=OPEN AI KEY
SERVER_PORT=8080
SERVER_IP=0.0.0.0
```

The server is now fully setup and ready to be used as listed in the [Usage Section](#usage).

## Client Setup

This section can be skipped if the user has received the set up animal already.

This project requires a [Raspberry Pi 4](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) and [WM8960 Audio Hat](https://www.waveshare.com/wm8960-audio-hat.htm). Run all necessary hardware driver installations.

Run ```pip install -r requirements-client.txt``` to install all necessary packages on the Raspberry Pi.

### USB Mounting Setup
To enable network configuration via USB flash drive through automatic mounting at startup:
1. Plug in the USB to the RPI.
2. Create a folder to mount through ```sudo mkdir /mnt/volume```.
3. Set proper permissions with ```sudo chmod 770 /mnt/volume```.
4. Mount the USB drive with ```sudo mount /dev/sda1 /mnt/volume```.
5. Configure your fstab by adding ```/dev/sda1 /mnt/volume ntfs defaults 0 2``` to the end of ```/etc/fstab```.
6. Reboot with ```sudo reboot```.

More information on this process can be found [here](https://gist.github.com/etes/aa76a6e9c80579872e5f).

### Running on RPI Startup

Add a call to ```rpi_boot.py``` in ```/etc/rc.local``` to enable running the program on boot.

# Usage

This usage setup assumes you have done the full setup for launching the game on RPI startup.

1. Connect the computer you intend to use to a Network. (Use Hotspot on campus to avoid Eduroam issues).
2. Find your systems IPv4 address ([Mac](https://www.security.org/vpn/find-mac-ip-address/)) ([Windows](https://support.microsoft.com/en-us/windows/find-your-ip-address-in-windows-f21a9bbc-c582-55cd-35e0-73431160a1b9)) ([Linux](https://phoenixnap.com/kb/how-to-find-ip-address-linux)).
3. Plug in the USB drive and edit the ```network_config.json``` file by setting the WiFi SSID, WiFi password, and IPv4 at the server_ip element. Make sure the network configurations are properly saved. There are times when ejecting can clear out all edited forms.
4. Plug the USB drive into the RPI. The RPI should be OFF right now.
5. Make sure your ```.env``` file is set up properly as described in the [server setup](#server-setup).
6. Start the server on your local machine through ```python src/game_server.py -ip IPv4_HERE```.
7. Power on the RPI and begin playing. There may be a bit of a delay as the RPI startups (2-3mins).

## Local Debugging

Use the ```-d``` flag to run local debug mode.

If you are running the client code, use ```python src/rpi_boot.py``` to begin testing.


# Code Information

The main body of our code is located in the src folder. Below is a brief description of each file:

```constants.py``` - This file holds global constants for our main routine. The most essential values are the timing between recording user inputs and the probability of game-ending prompts. 

```game_client.py``` -
  Driver code to run the game on the Raspberry Pi. 

```game_server.py``` -
   Driver code for the game to run on the computer, including calls to the LLM.

```helper.py``` -
  Includes testing protocols and assists in file loading.

```llm_handler.py``` -
  A file that calls OpenAI and relays prompts to and from ChatGPT.

```play_and_record_audio.py``` -
  Controls our system's microphone and speakers. 

```signals.py``` -
  Enumeration of critical signals including sending files and ending the game.

```speech_to_text.py``` -
  Translates user audio to text using vosk and stores it in a JSON file. This file is then processed by the LLM.

  ```tcp_file_transfer.py``` -
  TCP server and client structure/protocol. 

  ```text_to_speech.py``` -
  Converts text-file from the API to speech in the toy's voice.

  ```rpi_boot.py``` -
  Initiates Wi-Fi and the client code on the Raspberry Pi.

The IMU folder (within src) contains the software backend for the implementation of kinematic controls.

  ```IMU.py``` - 
  Driver code for Berry IMU v3 detection and measurements.

  ```LIS3MDL.py``` and ```LSM6DSL.py``` - 
  Addresses for reading from the IMU.

  ```berryIMU.py``` - 
  Contains different filters and improvements for IMU data.

  ```calibrateBerryIMU.py``` - 
  Runs calibration script to get maximum values in each dimension.

  ```imu_handler.py``` - 
  Top level IMU file that initializes IMU and has left/right and shake detection algorithms.

The data folder contains code for the configuration of our game:

```filtered_words.json``` -
Simplifies possible outputs from the API to vocabulary appropriate for a child

```prompts.json``` -
Converts user inputs/choices to appropriate responses by sending designated prompts to the API based on previous actions. 

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


The necessary packages for our system are located in ```requirements-client.txt``` and ```requirements-server.txt```.


  
  



  


  
  

