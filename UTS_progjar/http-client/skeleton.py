import socket
import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock

def get_first_length(data):
    header, _, body = data.partition('\r\n\r\n')
    content_length = header.split('Content-Length: ')[-1].split('\r\n')[0]
    try:
        return len(header) + int(content_length)
    except ValueError:
        return len(header)

def create_socket():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8080))
    return sock

def client():
    sock = create_socket()
    request = (f"GET index.html HTTP/1.1\r\n"
               f"Host: localhost\r\n\r\n" 
            )
    sock.send(request.encode())
    
    response = b''
    while True:
        chunk = sock.recv(1024)
        if not chunk:
            break
        response += chunk
        if len(response) < 1024:
            break
    
    response = response.decode()
    print(response, end='') 
    print()
    sock.close()

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
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]))

    def test_get_first_length_with_content_length(self):
        print('Testing get_first_length_with_content_length ...')
        data = "HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345"
        assert_equal(get_first_length(data), len(data.split('\r\n\r\n')[0]) + 5)

    @patch('socket.socket')
    def test_create_socket(self, mock_socket):
        print('Testing create_socket ...')
        create_socket()
        mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        instance = mock_socket.return_value
        instance.connect.assert_called_once_with(('localhost', 8080))
        print(f"connect called with: {instance.connect.call_args}")

    @patch('socket.socket')
    def test_client(self, mock_socket):
        print('Testing client ...')
        # Setup the mock socket
        mock_sock_instance = MagicMock()
        mock_socket.return_value = mock_sock_instance
        mock_sock_instance.recv.side_effect = [b'HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\n12345', b'']

        # Call the client function
        client()

        # Check socket methods were called correctly
        mock_sock_instance.connect.assert_called_with(('localhost', 8080))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called_once()  # Ensure 'recv' was called
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        mock_sock_instance.close.assert_called_once()
        print(f"close called with: {mock_sock_instance.close.call_args}")


if __name__ == '__main__':
    # Ong
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        client()

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
    
