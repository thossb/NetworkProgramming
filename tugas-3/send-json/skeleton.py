import socket
import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock
import json


def post_data(data):
    host = 'httpbin.org'
    port = 80

    # Convert the data to JSON format
    json_data = json.dumps(data)

    request = f"POST /post HTTP/1.1\r\n"
    request += f"Host: {host}\r\n"
    request += "Content-Type: application/json\r\n"
    request += f"Content-Length: {len(json_data)}\r\n"
    request += f"Connection: close\r\n\r\n"
    request += json_data

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(request.encode())

        response = b''
        while True:
            data = s.recv(1024)
            if not data:
                break
            response += data

    # Extract the JSON response body
    response_text = response.decode('utf-8')
    response_body = response_text.split('\r\n\r\n')[-1]
    return response_body



# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestPostData(unittest.TestCase):
    @patch('socket.socket')
    def test_post_data(self, mock_socket):
        # Setup the mocked socket instance
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        response_body = {"received": "ok", "status": "success"}
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Length: {}\r\n"
            "\r\n"
            "{}".format(len(json.dumps(response_body)), json.dumps(response_body))
        )
        mock_sock_instance.recv.side_effect = [http_response.encode('utf-8'), b'']

        # Call the function
        data = {"name": "John Doe", "age": 30}
        body = post_data(data)

        # Assertions to check if the response body is correctly returned
        mock_sock_instance.connect.assert_called_once_with(('httpbin.org', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        assert_equal(body, json.dumps(response_body))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        data = {"name": "John Doe", "age": 30}
        return_data = post_data(data)
        print(return_data)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
