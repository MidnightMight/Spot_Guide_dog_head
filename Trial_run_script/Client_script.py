# This is for the client device. 
# be it either the laptop or a micro controller with internet connectivity.
#
# Developed by: Michael V.
# Developed as a part of Spot Robotic guide dog head development project thesis for QCR QUT
# Date: 2025-07-25


import socket
import time
from threading import Thread as thread  # Use Thread for receiving messages

# Current goal: create a udp client that send commands to a server
# Open wrt
# SERVER_IP = '192.168.1.168' # Uncomment this line to use the local IP address 
# SERVER_IP = '192.168.0.213' # Home wifi
#Robot wifi IP for pi
SERVER_IP = '192.168.80.102' # Uncomment this line to use the local IP address
SERVER_PORT = 5005
UDP_Server = SERVER_IP
UDP_Port = SERVER_PORT



client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
# client.bind(("localhost", 5005))  # No need to bind for UDP client, OS will assign a port
name = input("Enter your nickname: ")  # Get nickname from user
client.sendto(f"nickname:{name}".encode(), (UDP_Server, UDP_Port))  # Send nickname to server
# Wait for server to acknowledge connection
time.sleep(1)  # Wait for a moment to ensure the server is ready
if response := client.recvfrom(1024):  # Receive acknowledgment from server
    print(f"Connected to server {UDP_Server} on port {UDP_Port}")
    print(f"Server acknowledgment: {response[0].decode()}")

def receive():
    while True:
        try:
            data, _ = client.recvfrom(1024)  # Buffer size is 1024 bytes
            msg = data.decode()
            if msg:
                print(f"\n{msg}")  # Print the received message
            else:
                print("Received empty message.")
            if data.decode().startswith("Server shutting down..."):
                # print("Server is shutting down. Exiting...")
                client.close()
                break
        except :
            pass

t = thread(target=receive).start()  # Start the receive thread
while True:
    try:
        Message = input("Enter message to send (or 'exit' to quit): ")  # Get message from user
        if Message.lower() == 'exit':
            print("Exiting...")
            client.sendto(f"{name} has left the chat.".encode(), (UDP_Server, UDP_Port))
            client.close()
            exit(1)
        client.sendto(f"{name}:{Message}".encode(), (UDP_Server, UDP_Port))  # Send message to server
    except KeyboardInterrupt:
        print("Exiting due to keyboard interrupt.")
        break
