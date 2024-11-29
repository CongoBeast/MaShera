# import socket

# def start_server(host='192.168.137.135', port=5000, filename='Revenue.txt'):
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#         server_socket.bind((host, port))
#         server_socket.listen()
#         print(f"Server listening on {host}:{port}")
        
#         conn, addr = server_socket.accept()
#         with conn:
#             print(f"Connected by {addr}")
#             with open(filename, 'rb') as f:
#                 while (chunk := f.read(1024)):
#                     conn.sendall(chunk)
#             print("File sent successfully.")

# if __name__ == "__main__":
#     start_server()
import socket
import threading
import os

clients = []

def handle_client(client_socket, addr):
    try:
        print(f"Connection from {addr} established.")
        
        # Receive file metadata
        filename = client_socket.recv(1024).decode('utf-8')
        filesize = int(client_socket.recv(1024).decode('utf-8'))
        
        # Save the received file
        with open(f"uploads/{filename}", 'wb') as f:
            received_size = 0
            while received_size < filesize:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
                received_size += len(data)
        
        print(f"File {filename} received and saved.")
        
        # Share the file with other clients
        for c in clients:
            if c != client_socket:
                try:
                    c.sendall(f"{filename}".encode('utf-8'))
                    c.sendall(str(filesize).encode('utf-8'))
                    with open(f"uploads/{filename}", 'rb') as f:
                        while (chunk := f.read(1024)):
                            c.sendall(chunk)
                    print(f"File {filename} sent to {c.getpeername()}.")
                except Exception as e:
                    print(f"Error sending file to {c.getpeername()}: {e}")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"Connection from {addr} closed.")

def start_server(host='192.168.137.135', port=5000):
    os.makedirs('uploads', exist_ok=True)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")
        
        while True:
            client_socket, addr = server_socket.accept()
            clients.append(client_socket)
            threading.Thread(target=handle_client, args=(client_socket, addr)).start()

if __name__ == "__main__":
    start_server()
