# import socket

# def start_client(host='192.168.137.135', port=5000, output_file='received_file.txt'):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
#         client_socket.connect((host, port))
#         print(f"Connected to server {host}:{port}")
        
#         with open(output_file, 'wb') as f:
#             while True:
#                 data = client_socket.recv(1024)
#                 if not data:
#                     break
#                 f.write(data)
#         print(f"File received and saved as {output_file}.")

# if __name__ == "__main__":
#     start_client()
import socket
import os
import time

def send_file(client_socket, filepath):
    filename = os.path.basename(filepath)
    filesize = os.path.getsize(filepath)

    print(filesize)
    
    # # Send file metadata
    # client_socket.sendall(filename.encode('utf-8'))
    # client_socket.sendall(str(filesize).encode('utf-8'))

    client_socket.sendall(f"{filesize}|{filename}".encode('utf-8'))

    time.sleep(5)
    
    # Send the file content
    with open(filepath, 'rb') as f:
        while (chunk := f.read(1024)):
            client_socket.sendall(chunk)
    
    print(f"File {filename} uploaded successfully.")

def start_client(host='192.168.137.135', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        
        # Select and send file
        filepath = input("Enter the file path to upload: ").strip()
        if os.path.exists(filepath):
            send_file(client_socket, filepath)
        else:
            print("File does not exist.")

if __name__ == "__main__":
    start_client()
