
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
from bosdyn.client import create_standard_sdk
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
import bosdyn.client.util

# Import the command interpreter for Spot
from Serial_to_spotSDK import Command_to_head_movement, send_to_servo_interface, inverse_kinematics,calibrate_head_movement

## Note: this script is designed to run on a Raspberry Pi connected to Spot via a Lan.
# It uses UDP to receive commands from a laptop or microcontroller to control Spot's head movement.

# Created by: Michael V.
# Date: 28-07-2025

def send_to_servo_interface(vx, vy, vr):
    """Send velocity command to the servo interface.
    Args:
        vx: Linear velocity in x direction (m/s).
        vy: Linear velocity in y direction (m/s).
        vr: Angular velocity (rad/s).
    """
    # Implement the logic to send the command to the servo interface
    # I2C to servo driver board. -> turn head and articulate if possible
    # This is a placeholder function. You need to implement the actual logic.
    print(f"Sending to servo interface: Estimated vx: {vx}, vy: {vy}, vr: {vr}")
    return

def send_velocity(robot_command_client, vx, vy, vr, duration=2.0):
    """Send velocity command to the robot.
    Args:
        robot_command_client: The RobotCommandClient instance.
        vx: Linear velocity in x direction (m/s).
        vy: Linear velocity in y direction (m/s).
        vr: Angular velocity (rad/s).
        duration: Duration to send the command (seconds). [Default: 2.0]
    """
    # check if it's a raspberry pi executing the code
    # if sys.platform == "linux":

    command = RobotCommandBuilder.synchro_velocity_command(vx, vy, vr)
    robot_command_client.robot_command(command, end_time_secs=time.time() + duration)

def stand_look_around(robot_command_client, duration=2.0, yaw_deg=0.0,pitch_deg=0.0):
    """Send stand and look around command to the robot.
    Args:
        robot_command_client: The RobotCommandClient instance.
        duration: Duration to send the command (seconds). [Default: 2.0]
    """
    footprint_R_body = bosdyn.geometry.EulerZXY(yaw=np.deg2rad(yaw_deg), roll=0.0, pitch=np.deg2rad(pitch_deg))
    cmd = RobotCommandBuilder.synchro_stand_command(footprint_R_body=footprint_R_body)
    robot_command_client.robot_command(cmd)

def Robot_movement(client, vx, vy, vr, duration=2.0, head_movement=True, head_delay = 0.2):
    """Send velocity command to the robot and move head.
    Args:
        client: The RobotCommandClient instance.
        vx: Linear velocity in x direction (m/s).
        vy: Linear velocity in y direction (m/s).
        vr: Angular velocity (rad/s).
    """
    command = RobotCommandBuilder.synchro_velocity_command(vx, vy, vr)
    if head_movement:
        send_to_servo_interface(vx, vy, vr)  # Send command to servo interface for head movement
        time.sleep(head_delay)  # Wait for the command to be sent
    # Send the command to the robot
    client.robot_command(command, end_time_secs=time.time() + duration)


###################### Code from Pi_servo_interface.py ######################

import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit
import numpy as np

def Servo_smooth(servo_obj,servo_no, Prev_angle, Target_angle, Duration, steps):
	# This function is liner profile for the servo angle smoothness.
	# This function is working with PCA9685 where the angle of the servo is not known due to i2c board.
	# Time step should be an integer in seconds.
	
	# Developed on the 16/07/2025 by Michael V.

	Step_angle = (Target_angle - Prev_angle) /steps 
	steps_duration = Duration/steps
	for step in range(1,steps):
		next_angle = (Prev_angle + (Step_angle)*step)
		print(next_angle)
		for servo in servo_no:
			servo_obj.servo[servo].angle = next_angle
		time.sleep(steps_duration)
		
	
	return Target_angle
def Servo_smooth_2(servo_obj,servo_no, Prev_angle, Target_angle, Duration, steps_per_sec):
	# This function is liner profile for the servo angle smoothness.
	# This function is working with PCA9685 where the angle of the servo is not known due to i2c board.
	# Time step should be an integer in seconds.
	
	# Developed on the 16/07/2025 by Michael V.
	steps = steps_per_sec * Duration

	Step_angle = (Target_angle - Prev_angle) /steps 
	steps_duration = Duration/steps
	for step in range(1,steps):
		next_angle = (Prev_angle + (Step_angle)*step)
		print(next_angle)
		for servo in servo_no:
			servo_obj.servo[servo].angle = next_angle
		time.sleep(steps_duration)
		
	
	return Target_angle

# Usage from pi script
kit = ServoKit(channels=16, i2c=busio.I2C(board.SCL, board.SDA))
kit.servo(4,5,6) # Initialize the servos on channels 4, 5, and 6