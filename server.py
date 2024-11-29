import socket

def start_server(host='192.168.137.135', port=5000, filename='Revenue.txt'):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))
        server_socket.listen()
        print(f"Server listening on {host}:{port}")
        
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            with open(filename, 'rb') as f:
                while (chunk := f.read(1024)):
                    conn.sendall(chunk)
            print("File sent successfully.")

if __name__ == "__main__":
    start_server()
