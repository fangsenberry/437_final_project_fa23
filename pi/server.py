import socket
import subprocess

def udp_server():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Bind the socket to a specific IP address and port
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)

    print('UDP server is running. Listening for messages...')

    recognition_process = None

    while True:
        # Receive a message and the client address
        message, client_address = server_socket.recvfrom(1024)
        message = message.decode()

        if message == '1':
            print('Received binary 1 from', client_address)
            # Start recognition.py if not already running
            if recognition_process is None:
                recognition_process = subprocess.Popen(["bash", "start_recognition.sh"])

        elif message == '0':
            print('Received binary 0 from', client_address)
            # Handle binary 0 message

        elif message == 'quit':
            print('Received quit message from', client_address)
            if recognition_process is not None:
                subprocess.call(["bash", "stop_recognition.sh"])
                recognition_process = None
            break

    # Close the socket
    server_socket.close()

# Run the UDP server
udp_server()
