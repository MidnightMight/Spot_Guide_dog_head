import time
import numpy as np
import sys

# Function for reading from the XB Serial module
def Serial_XB_read():
    """
    Simulate reading from a serial module.
    Replace this with actual serial reading code.
    Returns:
        A single character indicating the direction to head into.
    """
    # Placeholder: Always return 'f' for forward
    # In actual implementation, read from the serial port
    return 'f'  # Example: 'f' for forward, 'b' for backward, etc.

# Function for Joystick serial to head movement
def joystick_to_head_movement(Serial_command):
    movement_commands = {
        'f': Inverse_Kinematics(0, 1, 0),  # Forward
        'b': Inverse_Kinematics(0, -1, 0),  # Backward
        'l': Inverse_Kinematics(-1, 0, 0),  # Left
        'r': Inverse_Kinematics(1, 0, 0),   # Right"
    }
    # Robot will recieve serial command of a single letter indicating the direction to head into.
    movement = movement_commands.get(Serial_command, "Invalid command")

    # The command will be a single letter indicating the direction to head into.

    # The command will be sent to the servo interface via i2c.



# Sub-function calculate via Inverse Kinematics
    # Code from EGB339 developed.
def Inverse_Kinematics(x, y, z):
    """
    Calculate the inverse kinematics for head movement.
    Args:
        x: X coordinate (float).
        y: Y coordinate (float).
        z: Z coordinate (float).
    Returns:
        A tuple representing the angles for the head movement.
    """
    servo_length = 0.1  # Example length of the servo arm in meters
    Servo_1 = np.arctan2(y, x)  # Angle for servo 1
    Servo_2 = np.arctan2(z, np.sqrt(x**2 + y**2))  # Angle for servo 2
    Servo_1 = np.degrees(Servo_1)  # Convert to degrees
    Servo_2 = np.degrees(Servo_2)  # Convert to degrees
    # Ensure angles are within the range of -180 to 180 degrees
    Servo_1 = (Servo_1 + 180) % 360 - 180
    Servo_2 = (Servo_2 + 180) % 360 - 180

    return [Servo_1, Servo_2]  # Replace with actual servo angles




# Function for executing the head movement based on joystick input

# Function to communicate with the servo interface i2c from pi 5

# Calibration function for the head movement
def calibrate_head_movement():
    """
    Calibrate the head movement.
    This function can be used to set initial angles or perform calibration routines.
    """
    # Placeholder for calibration logic
    print("Calibrating head movement...")  # Replace with actual calibration logic
    # Verify max left heading
    Servo_1 = 15  # Example angle for max left heading
    # Verify max right heading
    Servo_1 = 165  # Example angle for max right heading
    # Verify max up heading
    Servo_2 =15  # Example angle for max up heading
    # Verify max down heading
    Servo_2 = 165
    print("Calibration complete.")
    
    # Move to default position
    Servo_1_default = 90  # Default angle for servo 1
    Servo_2_default = 90  # Default angle for servo 2

    return True  # Return True if calibration is successful, False otherwise