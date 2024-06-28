import socket
from unittest.mock import Mock, call, patch
import unittest
from io import StringIO

def handle_client(client_socket):
    # Send the welcome message
    client_socket.send(b'220 Welcome to Simple SMTP Server\r\n')
    
    # Receive and process commands
    while True:
        # Receive the command
        data = client_socket.recv(1024)
        if not data:
            break
        
        # print(f'Received: {data.strip()}')
        
        command = data.strip().decode()
        print(f'Received: {command}')

        # Send the response
        # if data starts with 'EHLO'  send '250 Hello\r\n'
        # etc.
        if command.startswith('EHLO') or command.startswith('HELO'):
            response = b'250 Hello\r\n'
        elif command.startswith('MAIL FROM:'):
            response = b'250 OK\r\n'
        elif command.startswith('RCPT TO:'):
            response = b'250 OK\r\n'
        elif command == 'DATA':
            response = b'354 End data with <CR><LF>.<CR><LF>\r\n'
        elif command == '.':
            response = b'250 OK: message accepted for delivery\r\n'
        elif command == 'QUIT':
            response = b'221 Bye\r\n'
            client_socket.send(response)
            break
        else:
            response = b'500 Syntax error, command unrecognized\r\n'

        client_socket.send(response)
    # close the socket
    client_socket.close()

def start_smtp_server(address='localhost', port=1025):
    # create a socket, bind it to the address and port, and start listening
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((address, port))
    server_socket.listen(1)
    print(f'Starting SMTP server on {address}:{port}')

    while True:
        # accept a connection
        client_socket, client_address = server_socket.accept()
        print(f'Accepted connection from {client_address}')

        # handle the client
        handle_client(client_socket)

# A 'null' stream that discards anything written to it
class NullWriter(StringIO):
    def write(self, txt):
        pass

class TestSMTPServer(unittest.TestCase):

    @patch('socket.socket')
    def test_handle_client(self, mock_socket):
        # Mock the client socket
        mock_client_socket = Mock()

        # Simulate a sequence of client commands and expected responses
        command_response_pairs = [
            (b'EHLO example.com\r\n', b'250 Hello\r\n'),
            (b'MAIL FROM:<test@example.com>\r\n', b'250 OK\r\n'),
            (b'RCPT TO:<recipient@example.com>\r\n', b'250 OK\r\n'),
            (b'DATA\r\n', b'354 End data with <CR><LF>.<CR><LF>\r\n'),
            (b'.\r\n', b'250 OK: message accepted for delivery\r\n'),
            (b'QUIT\r\n', b'221 Bye\r\n'),
        ]

        # Configure the mock to return each command in sequence when recv is called
        mock_client_socket.recv.side_effect = [command for command, _ in command_response_pairs] + [b'']

        # Call the handle_client function with the mock socket
        handle_client(mock_client_socket)

        # Check that send was called with the expected responses
        expected_calls = [call(response) for _, response in command_response_pairs]
        mock_client_socket.send.assert_has_calls(expected_calls, any_order=False)
        print(f"sending calls: {mock_client_socket.send.call_args_list}")

        # Check that the socket was closed
        mock_client_socket.close.assert_called_once()
        print(f"closing calls: {mock_client_socket.close.call_args_list}")

if __name__ == '__main__':
    runner = unittest.TextTestRunner(stream=NullWriter())
    unittest.main(testRunner=runner, exit=False)
