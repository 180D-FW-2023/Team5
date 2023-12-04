import socket


class FileTransferClient:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        self.close_connection()

    def connect_to_server(self):
        try:
            self.tcp_client_socket.connect((self.server_ip, self.server_port))
            print(f"Connected to server at {self.server_ip}:{self.server_port}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
            raise

    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                self.tcp_client_socket.sendall(file_data)
            print(f"File {file_path} sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")

    def receive_file(self, save_path):
        try:
            with open(save_path, 'wb') as file:
                data = self.tcp_client_socket.recv(1024)
                while data:
                    file.write(data)
                    data = self.tcp_client_socket.recv(1024)
            print(f"File received and saved at {save_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def close_connection(self):
        self.tcp_client_socket.close()
        print("Connection closed.")

class FileTransferServer:
    def __init__(self, server_ip, server_port):
        self.server_ip = server_ip
        self.server_port = server_port
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __del__(self):
        self.close_connection()

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

    def receive_file(self, save_path):
        try:
            with open(save_path, 'wb') as file:
                data = self.tcp_client_socket.recv(1024)
                while data:
                    file.write(data)
                    data = self.tcp_client_socket.recv(1024)
            print(f"File received and saved at {save_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def send_file(self, file_path):
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
                self.tcp_client_socket.sendall(file_data)
            print(f"File {file_path} sent successfully.")
        except Exception as e:
            print(f"Error sending file: {e}")

    def close_connection(self):
        self.tcp_client_socket.close()
        self.tcp_server_socket.close()
        print("Connection closed.")
