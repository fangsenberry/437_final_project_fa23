import socket

def udp_server():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a specific IP address and port
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)

    print('UDP server is running. Listening for messages...')

    while True:
        # Receive a message and the client address
        message, client_address = server_socket.recvfrom(1024)
        message = message.decode()

        if message == '1':
            print('Received binary 1 from', client_address)
            # Handle binary 1 message

        elif message == '0':
            print('Received binary 0 from', client_address)
            # Handle binary 0 message

        elif message == 'quit':
            print('Received quit message from', client_address)
            break

    # Close the socket
    server_socket.close()

# Run the UDP server
udp_server()
