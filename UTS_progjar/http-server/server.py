import os
import socket
import threading
import select

config = {}
with open('httpserver.conf', 'r') as f:
    for line in f:
        name, value = line.strip().split('=')
        config[name] = value

HOST = '' 
PORT = int(config.get('PORT'))

index_file = 'index.html'
not_found_file = '404.html'
dataset_dir = 'dataset'

# Read HTML content
def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return None

index_content = read_file(index_file)
not_found_content = read_file(not_found_file)

def handle_client(client_socket):
    request = client_socket.recv(1024).decode()
    print(f"Request:\n{request}")

    if request:
        lines = request.split('\n')
        if lines:
            request_line = lines[0]
            parts = request_line.split()
            if len(parts) >= 2:
                method, path = parts[0], parts[1]
                if method == 'GET':
                    if path == '/':
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{index_content}"
                    elif os.path.isfile('.' + path):
                        file_path = '.' + path
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n".encode() + file_content
                    elif os.path.isdir('.' + path):
                        dir_path = '.' + path
                        dir_listing = '\n'.join(os.listdir(dir_path))
                        response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\n{dir_listing}"
                    else:
                        response = f"HTTP/1.1 404 Not Found\r\nContent-Type: text/html\r\n\r\n{not_found_content}"
                    
                    client_socket.sendall(response.encode() if isinstance(response, str) else response)
    
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Serving HTTP on port {PORT}...")

    inputs = [server_socket]
    while True:
        readable, writable, exceptional = select.select(inputs, [], inputs)
        for s in readable:
            if s is server_socket:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()

if __name__ == "__main__":
    # Ong
    main()
