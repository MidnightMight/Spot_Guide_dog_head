import time
import numpy as np
import sys
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

## Code start here

def message_parser(message):
    """
    Parse the incoming message to determine the head movement command.
    Args:
        message: A string containing the command.
    Returns:
        A single character indicating the direction to head into.
    """
    
    movement_commands = {
        'f': 'f',  # Forward
        'b': 'b',  # Backward
        'l': 'l',  # Left
        'r': 'r',  # Right
        'w': 'w',  # Up
        's': 's',  # Down
        'a': 'a',  # Left
        'd': 'd'   # Right
    }
    # Check if the message is a valid command
    if message in movement_commands:
        return movement_commands[message]
    else:
        return None

# Function for recieved command to servo interface

def Servo_initialize():
    """
    Initialize the servo interface.
    This function sets up the servo kit for controlling the head movement.
    Returns:
        A ServoKit instance for controlling servos.
    """
    # Initialize the I2C bus
    i2c = busio.I2C(board.SCL, board.SDA)
    
    # Create a ServoKit instance with 16 channels
    kit = ServoKit(channels=16, i2c=i2c)
    
    # Set initial angles for servos
    kit.servo[0].angle = 90  # Servo 1
    kit.servo[1].angle = 90  # Servo 2
    
    print("Servo interface initialized.")
    
    return kit

def Servo_interface(kit, command, previous_command=None, Duration=1):
    """
    Send the command to the servo interface.
    Args:
        command: A single character indicating the direction to head into.
    """

    # Define servo angles based on command ** This is a placeholder for actual angles.

    angles = {
        'f': (90, 90),  # Forward
        'b': (90, 90),  # Backward
        'l': (45, 90),  # Left
        'r': (135, 90), # Right
        'w': (90, 45),  # Up
        's': (90, 135), # Down
        'a': (45, 90),  # Left
        'd': (135, 90)  # Right
    }
    if previous_command is None:
        previous_command = (90, 90)
    else:
        previous_command = angles[command]

    if command in angles:
        servo_1_angle, servo_2_angle = angles[command]
        Smooth_head_movement(kit, (servo_1_angle, servo_2_angle), previous_command, step=20)
        print(f"Moving head to: {servo_1_angle}, {servo_2_angle}")
    else:
        print("Invalid command received.")

def Smooth_head_movement(kit, target_angles, previous_angles=None, step=15):
    """
    Smoothly move the head to the target angles.
    Args:
        kit: The ServoKit instance for controlling servos.
        target_angles: A tuple of target angles for servo 1 and servo 2.
        previous_angles: A tuple of previous angles for servo 1 and servo 2 (optional).
        step: Amount of step in duration.
        duration: The total duration for the movement.
    """

    servo_1_start, servo_2_start = previous_angles
    servo_1_target, servo_2_target = target_angles

    # Calculate the number of steps based on the duration and step size
    num_steps = int(step)  # Convert step to seconds
    for i in range(num_steps + 1):
        # Calculate intermediate angles
        servo_1_angle = servo_1_start + (servo_1_target - servo_1_start) * i / num_steps
        servo_2_angle = servo_2_start + (servo_2_target - servo_2_start) * i / num_steps
        
        # Set the angles to the servos
        kit.servo[0].angle = servo_1_angle
        kit.servo[1].angle = servo_2_angle
        
        time.sleep(0.1)  # Sleep for the step duration





### Test code here import time
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
kit = ServoKit(channels = 16)
enable_list = (0,1)
kit.servo[0].angle = 110
kit.servo[1].angle = 85
time.sleep(1)
Servo_smooth(kit,(0,2),180,50,2,60)
#time.sleep(1)
#Servo_smooth(kit,(1,3),40,130,2,20)
#Servo_smooth_2(kit,(4,5),175,95,2,60)
#Servo_smooth_2(kit,(4,5),95,175,2,60)
#Servo_smooth(kit,(5,6),175,95,2,60)
#Servo_smooth(kit,(5,6),95,175,2,60)

