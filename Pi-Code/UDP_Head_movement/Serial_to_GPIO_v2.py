import time
import numpy as np
import sys
import board
import busio
from adafruit_pca9685 import PCA9685
from adafruit_servokit import ServoKit

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
    kit.servo[2].angle = 90
    
    print("Servo interface initialized.")
    
    return kit

# Calibration function for the head movement
def calibrate_head_movement(kit):
    """
    Calibrate the head movement.
    This function can be used to set initial angles or perform calibration routines.
    """
    # Placeholder for calibration logic
    print("Calibrating head movement...")  # Replace with actual calibration logic
    Delay = 2

    # Straight 110 , 50 down 180 up servo 0
    # left right 85 middle, 130 left, 40 right servo 1
    kit.servo[0].angle = 110
    kit.servo[1].angle = 85
    kit.servo[2].angle = 90
    time.sleep(Delay)

    # Left turn
    kit.servo[0].angle = 110
    kit.servo[1].angle = 130
    kit.servo[2].angle = 0

    time.sleep(Delay)

    kit.servo[0].angle = 110
    kit.servo[1].angle = 85
    time.sleep(Delay)

    # Right turn
    kit.servo[0].angle = 110
    kit.servo[1].angle = 40
    kit.servo[2].angle = 180
    time.sleep(Delay)

    # full sweep
    kit.servo[0].angle = 110
    kit.servo[1].angle = 130
    time.sleep(Delay)

    kit.servo[0].angle = 110
    kit.servo[1].angle = 85
    time.sleep(Delay)

    # Fully up
    kit.servo[0].angle = 180
    kit.servo[1].angle = 85
    time.sleep(Delay)

    kit.servo[0].angle = 110
    kit.servo[1].angle = 85
    time.sleep(Delay)

    # fully down
    kit.servo[0].angle = 50
    kit.servo[1].angle = 85
    time.sleep(Delay)

    # full sweep
    kit.servo[0].angle = 180
    kit.servo[1].angle = 85
    time.sleep(Delay)

    kit.servo[0].angle = 50
    kit.servo[1].angle = 130
    time.sleep(Delay)

    kit.servo[0].angle = 180
    kit.servo[1].angle = 130
    time.sleep(Delay)

    kit.servo[0].angle = 180
    kit.servo[1].angle = 85
    time.sleep(Delay)

    kit.servo[0].angle = 180
    kit.servo[1].angle = 40
    time.sleep(Delay)

    kit.servo[0].angle = 50
    kit.servo[1].angle = 40
    time.sleep(Delay)

    kit.servo[0].angle = 50
    kit.servo[1].angle = 85
    time.sleep(Delay)

    kit.servo[0].angle = 50
    kit.servo[1].angle = 130
    time.sleep(Delay)

    kit.servo[0].angle = 110
    kit.servo[1].angle = 85
    kit.servo[2].angle = 90
    time.sleep(Delay)
    
    return True  # Return True if calibration is successful, False otherwise

if __name__ == "__main__":
    # Initialize I2C bus and PCA9685 module.
    i2c = busio.I2C(board.SCL, board.SDA)
    pca = PCA9685(i2c)
    pca.frequency = 50

    # Initialize ServoKit instance for 16 channels.
    kit = ServoKit(channels=16, i2c=i2c)

    # Create an instance of the Head_movement_library
    head_movement = Head_movement_library(kit)

    # Calibrate head movement
    calibrate_head_movement(kit)

    # Move to default position
    head_movement.default_position()

    # Example usage of servo_smooth_turn
    head_movement.servo_smooth_turn(0, 180, steps=10, duration=2)  # Move servo 0 to 180 degrees smoothly
    head_movement.servo_smooth_turn([0, 1], [90, 45], steps=20, duration=3)  # Move both servos smoothly