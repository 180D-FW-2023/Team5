# file to handle all the boot configurations on an rpi
import os
import subprocess
import json
import sys
import time
from pathlib import Path

from game_client import GameClient
from constants import *

# change to parent directory to standard directories
os.chdir(Path(__file__).parent.parent.resolve())

def check_internet_connection():
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"])
        return True
    except subprocess.CalledProcessError:
        return False

def configure_wifi(ssid, password, timeout=None):
    wpa_supplicant_text = f"""
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US

    network={{
        ssid="{ssid}"
        psk="{password}"
        scan_ssid=1
    }}
    """

    #writing to file
    with open("temp_supplicant.conf", "w") as f:
        f.write(wpa_supplicant_text)
    #give access and writing. may have to do this manually beforehand
    subprocess.run(["sudo", "chmod", "a+w", "temp_supplicant.conf"])

    print("Wifi config added. Refreshing configs")
    # refresh configs
    subprocess.run(["sudo", "cp", "temp_supplicant.conf", "/etc/wpa_supplicant/wpa_supplicant.conf"])
    subprocess.run(["sudo", "wpa_cli", "-i",  "wlan0", "reconfigure"])
    subprocess.run(["sudo", "rm", "temp_supplicant.conf"])

    if timeout is None: # skips timeout
        return 

    start = time.time()
    while not check_internet_connection():
        if time.time() - start > timeout:
            sys.exit("Unable to connect to wifi. Aborting start.")
        time.sleep(.5)
    print("Wifi connected")

def main():
    with open(NETWORK_INIT_FILE_PATH, "r") as f:
        network_config = json.load(f)

    if check_internet_connection():
        print("Internet is connected.")
    else:
        print("Internet is not connected.")
        
    configure_wifi(network_config["ssid"], network_config["password"], timeout=15)

    # TODO: ADD RERUNS OF RUNNING THE CLIENT HERE/LOADING SAVED STATES
    game_client = GameClient(server_ip=network_config["server_ip"],
                             server_port=network_config["server_port"])
    game_client.main_loop()


if __name__ == "__main__":
    main()
