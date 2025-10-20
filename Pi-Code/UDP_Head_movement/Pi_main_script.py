
# UDP communication with Laptop or Microcontroller to control Spot's head movement
import socket
import time
from threading import Thread
import queue

# Import necessary libraries for the Spot robot client
import logging
import time
import numpy as np
import sys
import msvcrt
# from bosdyn.client import create_standard_sdk
# from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
# from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
# import bosdyn.client.util


## Note: this script is designed to run on a Raspberry Pi connected to Spot via a Lan.
# It uses UDP to receive commands from a laptop or microcontroller to control Spot's head movement.

# Created by: Michael V.
# Date: 28-07-2025
# Version: 1.0

# LAN port for Spot robot
# Spot_IP = "10.0.0.3" 


# Configuration for Spot robot movement
VELOCITY_LEVELS = [0.3, 0.5, 0.8]
speed_idx = 1
VELOCITY = VELOCITY_LEVELS[speed_idx]  # Set the default velocity level
ROTATION = 0.6  # Default rotation speed
e_stopped = False
standing = True  # Flag to check if Spot is standing

def Recieve_commands():

    # sdk = create_standard_sdk("SpotUDPServerClient")
    # robot = sdk.create_robot(Spot_IP)  # Create a robot instance with the Spot IP address

    # # Authenticate the robot
    # try:
    #     robot.authenticate('user', 'PWD')  # Replace with your credentials
    # except Exception as e:
    #     print(f"Authentication failed: {e}")
    #     return
    # bosdyn.client.util.authenticate(robot)  # Authenticate the robot using the SDK utility
    # robot.time_sync.wait_for_sync()  # Wait for time synchronization with the robot

    # # Ensure the RobotCommandClient is available
    # try:
    #     robot_command_client = robot.ensure_client(RobotCommandClient.default_service_name)
    # except Exception as e:
    #     print(f"Failed to create RobotCommandClient: {e}")
    #     return
    # # Ensure the LeaseClient is available
    # try:
    #     lease_client = robot.ensure_client(LeaseClient.default_service_name)
    # except Exception as e:
    #     print(f"Failed to create LeaseClient: {e}")
    #     return
    
    # # Take a lease on the robot
    # try:
    #     lease = lease_client.take()
    #     lease_keep_alive = LeaseKeepAlive(lease_client, must_acquire=True, return_at_exit=True)
    # except Exception as e:
    #     print(f"Failed to take lease: {e}")
    #     return
    
    # print("Powering on...")
    # robot.power_on()
    # print("Standing up...")
    # robot_command_client.robot_command(RobotCommandBuilder.selfright_command())
    # time.sleep(10)
    # robot_command_client.robot_command(RobotCommandBuilder.synchro_stand_command())
    # time.sleep(2)

    """Thread to receive commands from the UDP server."""
    while True:
        try:
            data, addr = server.recvfrom(1024)  # Buffer size is 1024 bytes
            command = data.decode().strip()
            print(f"Received command: {command} from {addr}")
            Command_to_head_movement(command)  # Process the received command
        except Exception as e:
            print(f"Error receiving command: {e}")


def get_local_ip():
    """Get the local IP address of the Raspberry Pi."""
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    return local_ip

# UDP server configuration
UDP_IP = get_local_ip()  # Use the local IP address of the Raspberry Pi
UDP_PORT = 5005  # Port to listen for incoming commands
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Create a UDP socket
server.bind((UDP_IP, UDP_PORT))  # Bind the socket to the IP and port
# Start the command receiving thread
receive_thread = Thread(target=Recieve_commands, daemon=True)
receive_thread.start()

## Main function to initialize the Spot robot and start the command loop

