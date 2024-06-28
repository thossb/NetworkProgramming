        # check for read-ready socket
        for sock in read_sockets:
            # if the read-ready socket is the client socket
            if sock == self.client_socket:
                # receive message
                message = self.client_socket.recv(1024)

                # write message to stdout
                sys.stdout.write(message.decode())
            else:
                # read message from readline
                message = sys.stdin.readline()

                # send message
                self.client_socket.send(message.encode())

                # flush the stdout
                sys.stdout.flush()