import socket

def start_client(host='192.168.137.135', port=5000, output_file='received_file.txt'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(f"Connected to server {host}:{port}")
        
        with open(output_file, 'wb') as f:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                f.write(data)
        print(f"File received and saved as {output_file}.")

if __name__ == "__main__":
    start_client()
