import socket
import time
from threading import Thread
import queue

messages = queue.Queue()
clients = []
log_messages = []

# Use the actual server IP address
# SERVER_IP = "192.168.0.213"
# SERVER_PORT = 5005
def get_local_ip():
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip
# If you want to use the local IP address instead of a hardcoded one
SERVER_IP = get_local_ip()  # Uncomment this line to use the local IP address dynamically
SERVER_PORT = 5005  # Replace with your server's port number
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

def receive():
    while True:
        try:
            data, addr = server.recvfrom(1024)
            messages.put((data, addr))
        except Exception as e:
            print(f"Receive error: {e}")

def broadcast():
    while True:
        if not messages.empty():
            data, addr = messages.get()
            msg = data.decode()
            print(msg)
            # Log every message as soon as it's processed
            log_messages.append(f"{addr}: {msg}")

            if addr not in clients:
                clients.append(addr)
            if msg.startswith("nickname:"):
                nickname = msg.split(":", 1)[1].strip()
                print(f"Client {addr} set nickname: {nickname}")
                server.sendto(f"Welcome! {nickname}".encode(), addr)
                for client in clients:
                    if client != addr:
                        server.sendto(f"{nickname} has joined the chat.".encode(), client)
            else:
                for client in clients:
                    try:
                        if client != addr:  # Don't send the message back to the sender
                            server.sendto(data, client)
                    except Exception as e:
                        print(f"Broadcast error to {client}: {e}")
                        clients.remove(client)

thread1 = Thread(target=receive, daemon=True)
thread2 = Thread(target=broadcast, daemon=True)
thread1.start()
thread2.start()
print(f"Server is running on {SERVER_IP}:{SERVER_PORT}...")
print("Waiting for clients to connect...")
print("Press Ctrl+C to stop the server.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Server shutting down...")
    for client in clients:
        try:
            server.sendto("Server is shutting down.".encode(), client)
        except Exception as e:
            print(f"Error sending shutdown message to {client}: {e}")
    # Save all logged messages to file
    with open("server_log.txt", "w", encoding="utf-8") as log_file:
        for entry in log_messages:
            log_file.write(entry + "\n")
    print("Saved messages to server_log.txt and exiting.")
    server.close()
