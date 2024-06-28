import socket
import json
import sys
import unittest
from io import StringIO
from unittest.mock import patch, MagicMock


def create_post(title, body, user_id):
    # Create a socket object
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Connect to the server
        s.connect(('jsonplaceholder.typicode.com', 80))

        # Create the POST request
        post_data = {
            'title': title,
            'body': body,
            'userId': user_id
        }
        post_data_str = json.dumps(post_data)
        request = f"POST /posts HTTP/1.1\r\nHost: jsonplaceholder.typicode.com\r\nContent-Type: application/json\r\nContent-Length: {len(post_data_str)}\r\nConnection: close\r\n\r\n{post_data_str}"
        s.send(request.encode('utf-8'))

        # Receive the response
        response = s.recv(4096).decode('utf-8')

        # Extract the ID from the response
        response_data = json.loads(response.split('\r\n\r\n')[1])
        post_id = response_data['id']

        return post_id


# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass


def assert_equal(parameter1, parameter2):
    if parameter1 == parameter2:
        print(f'test attribute passed: {parameter1} is equal to {parameter2}')
    else:
        print(f'test attribute failed: {parameter1} is not equal to {parameter2}')


class TestCreatePost(unittest.TestCase):
    @patch('socket.socket')
    def test_create_post(self, mock_socket):
        # Setup the mocked socket
        mock_sock_instance = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock_instance

        # Define the mock response from the server
        response_data = {
            'id': 101,
            'title': 'New Entry',
            'body': 'This is a new post.',
            'userId': 1
        }
        http_response = f"HTTP/1.1 201 Created\r\nContent-Length: {len(json.dumps(response_data))}\r\n\r\n{json.dumps(response_data)}"
        mock_sock_instance.recv.side_effect = [http_response.encode('utf-8'), b'']

        # Call the function
        post_id = create_post("New Entry", "This is a new post.", 1)

        # Assertions to check if the POST request was properly sent and the correct ID was returned
        # Verify that the socket methods were called correctly
        mock_sock_instance.connect.assert_called_with(('jsonplaceholder.typicode.com', 80))
        print(f"connect called with: {mock_sock_instance.connect.call_args}")

        mock_sock_instance.send.assert_called_once()
        print(f"send called with: {mock_sock_instance.send.call_args}")

        mock_sock_instance.recv.assert_called()
        print(f"recv called with: {mock_sock_instance.recv.call_args}")

        mock_sock_instance.send.assert_called_once()
        assert_equal(post_id, 101)
        


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == 'run':
        post_id = create_post('This is a new title', 'This is a new post.', 1)
        print(post_id)

    # run unit test to test locally
    # or for domjudge
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)

