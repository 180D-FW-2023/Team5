import socket
import os
import struct
import time

from abc import ABC, abstractmethod
# TODO: ADD TIMEOUTS


class TCPBase(ABC): # abstract class with functionality for sending and receiving files
    def __init__(self, server_ip, server_port, timeout=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_file(self, file_path, timeout=20):
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
        try:
            # Receive the file size
            size_data = self.tcp_client_socket.recv(4)
            file_size = struct.unpack("!I", size_data)[0]

            received_size = 0
            with open(save_path, 'wb') as file:
                while received_size < file_size:
                    data = self.tcp_client_socket.recv(1024)
                    if not data:
                        break
                    file.write(data)
                    received_size += len(data)

            print(f"File received and saved at {save_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")

    @abstractmethod
    def close_connection(self):
        pass

    def __del__(self):
        self.close_connection()

class FileTransferClient(TCPBase):
    def __init__(self, server_ip, server_port, timeout=None):
        super().__init__(server_ip, server_port, timeout)

    def connect_to_server(self):
        try:
            self.tcp_client_socket.connect((self.server_ip, self.server_port))
            print(f"Connected to server at {self.server_ip}:{self.server_port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            raise

    def close_connection(self):
        self.tcp_client_socket.close()
        print("Connection closed.")

class FileTransferServer(TCPBase):
    def __init__(self, server_ip, server_port, timeout=None):
        super().__init__(server_ip, server_port, timeout)
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start_server(self):
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
