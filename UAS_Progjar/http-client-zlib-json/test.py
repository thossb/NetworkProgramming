import socket
import sys
import unittest
import json
import zlib
from io import StringIO
from unittest.mock import MagicMock, patch

def get_first_length(data):
    """Get the length of the first part of the response, including the header and the content if Content-Length is present."""
    header_end = data.find("\r\n\r\n") + 4
    header = data[:header_end]
    content_length = 0
    for line in header.split("\r\n"):
        if line.startswith("Content-Length:"):
            content_length = int(line.split(":")[1].strip())
            break
    return header_end + content_length

def create_socket():
    """Create a client socket and connect to the server."""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8080))
    return client_socket

def client():
    """Send a GET request to the server and print the response."""
    # Create socket and send the request
    client_socket = create_socket()
    request = "GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n"
    client_socket.sendall(request.encode('utf-8'))

    # Receive the response
    response = b""
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        response += data

    # Decode and print the response
    response = response.decode('utf-8')

    # Get the status code
    status_line = response.split("\r\n")[0]
    status_code = int(status_line.split(' ')[1])

    # Print the status code
    if status_code == 200:
        print("Status: 200 OK")
    elif status_code == 404:
        print("Status: 404 Not Found")
    elif status_code == 500:
        print("Status: 500 Internal Server Error")

    # Close the socket
    client_socket.close()

    # Decompress and parse JSON content
    header_length = get_first_length(response)
    body = response[header_length:]
    decompressed_body = zlib.decompress(body.encode('latin1')).decode('utf-8')
    json_data = json.loads(decompressed_body)
    
    # Print the JSON content
    print(f"JSON Response: {json_data}")

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')

class TestHttpClient(unittest.TestCase):
    def test_get_first_length_no_content_length(self):
        print('Testing get_first_length_no_content_length ...')
        data = "HTTP/1.1 200 OK\r\nServer: TestServer\r\n\r\n"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 4)

    def test_get_first_length_with_content_length(self):
        print('Testing get_first_length_with_content_length ...')
        data = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 4 + 5)

    @patch('socket.socket')
    def test_create_socket(self, mock_socket):
        print('Testing create_socket ...')
        create_socket()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        instance = mock_socket.return_value
        instance.connect.assert_called_once_with(('localhost', 8080))
        print(f"connect called with: {instance.connect.call_args}")

if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        client()

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
