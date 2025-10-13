import socket
import time
from threading import Thread
import queue
import numpy as np
import sys
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

# This is for the Recieving and processing of UDP message device
# Made by: Michael V.
# Developed as a part of Spot Robotic guide dog head development project thesis for QCR QUT
# Date Updated: 4-10-2025
# =========================================================================================================================
# Version 1.5 (06-08-2025)
# - Implemented a UDP server that is a chat room but also execute commands for the head movement servos.
# - The server can handle multiple clients and broadcast messages to all connected clients.
# - Added logging functionality to save all messages to a text file upon server shutdown.
# - Improved error handling for socket operations.
# - The server initializes and calibrates the servo interface for head movement control.
# - Each command is executed in a separate thread to avoid blocking the main server loop.
# =========================================================================================================================
# Version 2.0 (Latest) (04-10-2025)
# - Updated the message parser to include more movement commands.
# - Improved the Servo_interface function to handle smooth transitions between commands.
# =========================================================================================================================

messages = queue.Queue()
clients = []
log_messages = []

server_ip = socket.gethostbyname(socket.gethostname())  # Get the local IP address dynamically

# Open wrt
# SERVER_IP = '192.168.1.168' # Uncomment this line to use the local IP address dynamically

#Robot wifi IP for pi
SERVER_IP = '192.168.80.102' # Uncomment this line to use the local IP address dynamically
SERVER_IP = '192.168.0.213'
SERVER_PORT = 5005

server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server.bind((SERVER_IP, SERVER_PORT))

from Serial_to_GPIO_v2 import calibrate_head_movement, Servo_initialize
class Head_movement_library:
    def message_parser(self,message):
        # Parse the incoming message and extract relevant information
        return {
                's': "Looking Center",  # Default position
                'w': "Looking Up",  # Look UP forward
                'x': "Looking Down",   # Look Down forward
                'a': "Looking Left", # Look Left
                'd': "Looking Right",   # Look Right
                'q': "Looking Up Left",    # Look Up Left
                'e': "Looking Up Right",    # Look Up Right
                'z': "Looking Down Left",   # Look Down Left
                'c': "Looking Down Right",    # Look Down Right
            }.get(message, None)  # Default position if command not found

    def Head_position_library(self,command):
        # Return default angles for the position from previous command
        # Dog head mapping s is center position while other letters are movement commands in reference to center position
        if command != 's':
            return {
                'w': (180, 85,90),  # Look UP forward
                'x': (50, 85,90),   # Look Down forward
                'a': (110, 130,0), # Look Left
                'd': (110, 40,180),   # Look Right
                'q': (180, 130,0),    # Look Up Left
                'e': (180, 40,180),    # Look Up Right
                'z': (50, 130,0),   # Look Down Left
                'c': (50, 40,180),    # Look Down Right
            }.get(command, (110, 85,90))  # Default position if command not found
        else:
            return (110, 85,90)  # Default position

    def __init__(self,kit):
         self.kit = kit
         self.previous_command = (110, 85,90)  # Initialize to default position
         print("Head movement library initialized.")
         return

    def default_position(self):
        Servo_0_default = 110  # Default angle for servo 1
        Servo_1_default = 85  # Default angle for servo 2
        Servo_2_default = 90
        self.kit.servo[0].angle = Servo_0_default
        self.kit.servo[1].angle = Servo_1_default
        self.kit.servo[2].angle = Servo_2_default
        self.previous_command = (Servo_0_default, Servo_1_default, Servo_2_default)
        print("Moved to default position.")
        return self.previous_command
    
    def command_to_servo(self,command):
        # Move the servos based on the command input
        angles = self.Head_position_library(command)
        self.servo_smooth_turn([0, 1, 2], angles, steps=45, duration=0.5)
        print(f"Command '{command}' executed. Moved to angles: {angles}")
        return angles
    
    def servo_smooth_turn(self,servo_no,angle_target,steps,duration=1):
        # Smooth turn for the servo assuming there is only two servo in use.
        # servo_no: int (0 or 1) or list/array of servo numbers
        # angle_target: int (single angle) or list/array of angles (must match servo_no length)
        try:
            steps = int(steps)
        except ValueError:
            print("Invalid steps. Please enter a valid integer.")
            return None
        if steps <= 0:
            print("Steps must be a positive integer.")
            return None
            
        # Handle both single servo and multiple servos
        if isinstance(servo_no, (list, tuple, np.ndarray)):
            servo_list = list(servo_no)
            if isinstance(angle_target, (list, tuple, np.ndarray)):
                angle_list = list(angle_target)
                if len(servo_list) != len(angle_list):
                    print("Servo numbers and angle targets must have the same length.")
                    return None
            else:
                print("When servo_no is a list/array, angle_target must also be a list/array.")
                return None
                
            # Validate servo numbers and angles
            for i, (servo, angle) in enumerate(zip(servo_list, angle_list)):
                try:
                    servo_list[i] = int(servo)
                    angle_list[i] = int(angle)
                except ValueError:
                    print(f"Invalid servo number or angle at index {i}.")
                    return None
                if servo_list[i] not in [0, 1, 2]:
                    print(f"Invalid servo number {servo_list[i]}. Please enter 0, 1, or 2.")
                    return None
                    
            # Get starting angles for all servos
            angle_start_list = [self.previous_command[servo] for servo in servo_list]
            
        else:
            # Single servo case
            try:
                servo_no = int(servo_no)
                angle_target = int(angle_target)
            except ValueError:
                print("Invalid servo number or angle target. Please enter valid integers.")
                return None
            if servo_no not in [0, 1]:
                print("Invalid servo number. Please enter 0 or 1.")
                return None
                
            servo_list = [servo_no]
            angle_list = [angle_target]
            angle_start_list = [self.previous_command[servo_no]]
            
        # Calculate step sizes and sleep time
        sleep_time = duration / steps
        
        # Perform smooth movement with S-curve (sigmoid-like acceleration/deceleration)
        for step in range(1, steps + 1):
            # Calculate progress as a value between 0 and 1
            progress = step / steps
            
            # Apply S-curve transformation using sigmoid-like function
            # This creates smooth acceleration at start and deceleration at end
            s_curve_progress = 3 * progress**2 - 2 * progress**3
            
            for i, servo in enumerate(servo_list):
                next_angle = angle_start_list[i] + (angle_list[i] - angle_start_list[i]) * s_curve_progress
                self.kit.servo[servo].angle = next_angle
            time.sleep(sleep_time)
            
        # Update previous command
        current_angles = list(self.previous_command)
        for i, servo in enumerate(servo_list):
            current_angles[servo] = angle_list[i]
        self.previous_command = tuple(current_angles)
        return None
        



def receive():
    while True:
        try:
            data, addr = server.recvfrom(1024)
            messages.put((data, addr))
        except Exception as e:
            print(f"Receive error: {e}")

def broadcast():
    log_messages.append("Server started broadcasting messages.")
    # Initialize the servo interface
    kit = Servo_initialize()  # Initialize the servo kit
    # calibrate_head_movement(kit)  # Calibrate the head movement servos
    log_messages.append("Servo interface initialized and calibrated.")
    print("Servo interface initialized and calibrated.")
    head_movement_lib = Head_movement_library(kit)  # Create an instance of the head movement library
    # Start the main loop for broadcasting messages

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
            
            # Parse the message to get a reply
            msg = msg.split(":")[-1].strip()
            if not msg:  # If the message is empty, skip processing
                continue
            else:
                reply = head_movement_lib.message_parser(msg)  # Parse the message to get a reply
                if reply is None:
                    reply = "Invalid Char or Command"

                return_msg = ("Server:" + "Recieved " + reply).encode()  # acknowledge and encode the reply 
                data = return_msg  # Use the encoded message for broadcasting
            if addr not in clients:
                clients.append(addr)
            else:
                for client in clients:
                    try:
                        if client != addr:  # Don't send the message back to the sender
                            server.sendto(data, client)
                    except Exception as e:
                        print(f"Broadcast error to {client}: {e}")
                        clients.remove(client)
            
            # Execute the command if it's valid
            if reply != "Invalid Char or Command":
                print(f"Executing command: {reply}")
                # Here you would call the function to execute the command, e.g., joystick_to_head_movement(reply)
                # For now, we just print it
                thread_A = Thread(target=head_movement_lib.command_to_servo, args=(msg,), daemon=True)  # Send the command to the servo interface
                thread_A.start()  # Start the thread to execute the command
                # Spot SDK Thread to be done.
                # thread_B = Thread()

                thread_A.join()
                # Send the acknowledgment back to the client
                print(f"Command executed: {reply}")
                server.sendto(return_msg, addr)
                log_messages.append(f"Command executed: {reply}")

            else:
                print("Registered invalid command.")
            

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
