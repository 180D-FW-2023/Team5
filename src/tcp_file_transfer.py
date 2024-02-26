import socket
import os
import struct

import time

from abc import ABC, abstractmethod

from dotenv import load_dotenv

from signals import Signals
# TODO: ADD TIMEOUTS


class TCPBase(ABC): # abstract class with functionality for sending and receiving files
    def __init__(self, server_ip=None, server_port=None, timeout=None):
        if server_ip is None:
            print("SETTING SERVER IP TO 0.0.0.0 SINCE DOES NOT EXIST")
            self.server_ip = "0.0.0.0"
        if server_port is None:
            print("SETTING SERVER PORT TO 8080 SINCE DOES NOT EXIST")
            self.server_port = 8080

        self.server_ip = server_ip
        self.server_port = int(server_port)
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_signal(self, signal_data : int):
        # sends an int signal for quick communication across client/server
        signal_data = int(signal_data)
        signal = struct.pack("!I", signal_data)
        try:
            self.tcp_client_socket.sendall(signal)
            print(f"Signal {Signals(signal_data).name} sent successfully.")
        except Exception as e:
            print(f"Error sending signal: {e}")

    def receive_signal(self, expected_signals=[]):
        # receives an int signal for quick communication across client/server
        try:
            signal_data = self.tcp_client_socket.recv(4)
            signal = struct.unpack("!I", signal_data)[0]
            print(f"Signal {Signals(signal).name} received.")
        except Exception as e:
            print(f"Error receiving signal: {e}")
            return None

        if expected_signals != []:
            if signal not in expected_signals: # error checking
                raise Exception(f"Unaligned signals: Expected signals: {expected_signals} but received {signal}")
        return signal

    # send and receive data fns not currently used
    def send_data(self, data : str):

        self.send_signal(Signals.DATA_SENT)
        try:
            # Send the file size
            data_size = len(data)
            size_data = struct.pack("!I", data_size)
            self.tcp_client_socket.sendall(size_data)

            self.tcp_client_socket.sendall(data)

            print(f"Data {data[:20]}... sent successfully.")
        except Exception as e:
            print(f"Error sending data: {e}")

    def receive_data(self):
        received_data = ""
        try:
            # Receive the file size
            size_data = self.tcp_client_socket.recv(4)
            data_size = struct.unpack("!I", size_data)[0]

            received_size = 0
            while received_size < data_size:
                data = self.tcp_client_socket.recv(1024)
                if not data:
                    break
                received_data += data
                received_size += len(data)

            print(f"Data received including {received_data[:20]}...")
        except Exception as e:
            print(f"Error receiving data: {e}")
            return None

        return data

    def send_file(self, file_path):
        file_path = str(file_path) # for pathlib

        directory_path = os.path.dirname(file_path)
        contents = os.listdir(directory_path)
        print("Contents of directory:", directory_path)
        for item in contents:
            print(item)

        self.send_signal(Signals.FILE_SENT)
        try:
            # Send the file size
            file_size = os.path.getsize(file_path)
            size_data = struct.pack("!I", file_size)
            self.tcp_client_socket.sendall(size_data)

            with open(file_path, 'rb') as file:
                file_data = file.read()
                self.tcp_client_socket.sendall(file_data)

            print(f"File {file_path} sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_file(self, save_path):
        save_path = str(save_path) # for pathlib

        try:
            # Receive the file size
            size_data = self.tcp_client_socket.recv(4)
            file_size = struct.unpack("!I", size_data)[0]

            received_size = 0
            with open(save_path, 'wb') as file:
                while received_size < file_size:

                    packet_size = file_size - received_size if file_size - received_size < 1024 else 1024
                    data = self.tcp_client_socket.recv(packet_size)
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)

            print(f"File received and saved at {save_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")
            return None

        return save_path

    # not currently used, implemented separately in game_server
    def send_file_stream(self, input_queue):
        # assume the input queue is a queue of file paths

        self.send_signal(Signals.INIT_FT_STREAMED)
        while True:
            file_path = input_queue.get(timeout=10)
            if file_path is None:
                break

            self.send_file(file_path)

        self.send_signal(Signals.END_FT_STREAMED)

        pass

    def receive_file_stream(self, output_queue, save_dir, ext, file_name_tag=""):
        # sentinel is none
        save_dir.mkdir(exist_ok=True) # makes sure the save dir exists
        i = 0
        first_file = True
        while True:
            signal = self.receive_signal(expected_signals=[Signals.FILE_SENT, Signals.END_FT_STREAMED])
            if signal == Signals.END_FT_STREAMED:
                first_file = True # reset
                output_queue.put(None, timeout=10) # sentinel
                break
            received_file_path = self.receive_file(save_dir / f"{file_name_tag}_{i}{ext}")
            if first_file:
                end_time = time.time()
                print(f"\nJust received first file; ending time: {end_time}\n")
                first_file = False
            output_queue.put(received_file_path, timeout=10)
            i += 1


    @abstractmethod
    def close_connection(self):
        pass

    def __del__(self):
        self.close_connection()

class TCPClient(TCPBase):
    def __init__(self, server_ip=None, server_port=None, timeout=None):
        super().__init__(server_ip, server_port, timeout)

    def connect_to_server(self):
        try:
            print(str(self.server_ip), str(self.server_port))
            self.tcp_client_socket.connect((self.server_ip, self.server_port))
            print(f"Connected to server at {self.server_ip}:{self.server_port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            raise

    def close_connection(self):
        self.tcp_client_socket.close()
        print("Connection closed.")

class TCPServer(TCPBase):
    def __init__(self, server_ip=None, server_port=None, timeout=None):
        super().__init__(server_ip, server_port, timeout)
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
        print("start server function running")
        try:
            self.tcp_server_socket.bind((self.server_ip, self.server_port))
            self.tcp_server_socket.listen()
            print(f"Server listening on {self.server_ip}:{self.server_port}")

            # Accept a connection from a client
            self.tcp_client_socket, client_address = self.tcp_server_socket.accept()
            print(f"Accepted connection from {client_address}")
        except Exception as e:
            print(f"Error starting server: {e}")
            raise

    def close_connection(self):
        self.tcp_client_socket.close()
        self.tcp_server_socket.close()
        print("Connection closed.")
