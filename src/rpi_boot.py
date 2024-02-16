# file to handle all the boot configurations on an rpi
import subprocess
import json

from constants import *
def check_internet_connection():
    try:
        subprocess.check_output(["ping", "-c", "1", "8.8.8.8"])
        return True
    except subprocess.CalledProcessError:
        return False

def configure_wifi(ssid, password):
    config_lines = [
        'ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev',
        'update_config=1',
        'country=US',
        '\n',
        'network={',
        '\tssid="{}"'.format(ssid),
        '\tpsk="{}"'.format(password),
        '}'
        ]
    config = '\n'.join(config_lines)

    #give access and writing. may have to do this manually beforehand
    subprocess.run(["sudo", "chmod", "a+w", "/etc/wpa_supplicant/wpa_supplicant.conf"])

    #writing to file
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as wifi:
        wifi.write(config)

    print("Wifi config added. Refreshing configs")
    ## refresh configs
    subprocess.run(["sudo", "wpa_cli", "-i wlan0", "reconfigure"])

def main():
    if check_internet_connection():
        print("Internet is connected.")
    else:
        print("Internet is not connected.")
        with open(NETWORK_INIT_FILE_PATH, "r") as f:
            network_config = json.load(f)

        configure_wifi(network_config["ssid"], network_config["password"])

    # TODO: ADD RERUNS OF RUNNING THE CLIENT HERE/LOADING SAVED STATES


if __name__ == "__main__":
    main()
