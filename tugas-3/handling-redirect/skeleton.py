import socket
import sys
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch


def fetch_redirection_url():
    request = (
        f"GET /redirect-to?url=http://example.com HTTP/1.1\r\n"
        f"Host: httpbin.org\r\n"
        f"Connection: close\r\n"
        "\r\n"
    )
    
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        # Send the HTTP request
        sock.connect(('httpbin.org', 80))
        sock.send(request.encode())

        # Receive the response
        response = b''
        while True:
            chunk = sock.recv(1024)
            if not chunk:
                break
            response += chunk
        # response = sock.recv(4096)
        # print(response)
    sock.close()

    # print(response.decode())
    # Extract the URL from the response
    location = response.split(b'\r\n')[1]
    # print(location)
    url = location.decode().split(': ')[1]

    return url


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestFetchRedirectionUrl(unittest.TestCase):
    @patch('socket.socket')
    def test_fetch_redirection_url(self, mock_socket):
        # Setup the mocked socket instance
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        http_response = (
            "HTTP/1.1 302 Found\r\n"
            "Location: http://example.com\r\n"
            "\r\n"
        )
        mock_sock_instance.recv.side_effect = [http_response.encode('utf-8'), b'']

        # Call the function
        url = fetch_redirection_url()

        # Assertions to check if the correct URL was extracted
        mock_sock_instance.connect.assert_called_once_with(('httpbin.org', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        assert_equal(url, 'http://example.com')


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        url = fetch_redirection_url()
        print(url)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
