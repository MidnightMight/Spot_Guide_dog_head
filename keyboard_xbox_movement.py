# spot_nunchuck_controller.py

import time
import numpy as np
import sys
import msvcrt
from bosdyn.client import create_standard_sdk
from bosdyn.client.lease import LeaseClient, LeaseKeepAlive
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
import bosdyn.client.util

# Dummy nunchuck reader to simulate hardware input.
# Replace this with actual I2C/GPIO-based code for real controller.
def read_nunchuck():
    """
    Simulate reading from a nunchuck.
    Replace this with actual I2C code.
    z_btn: Z button (bool) # E-stop
    c_btn: C button (bool) # Speed cycle
    latch_btn: Latch button (bool) # Sit/stand
    lx: Left joystick x-axis (-1 to 1)
    ly: Left joystick y-axis (-1 to 1)
    Returns:
        (lx, ly, z_btn, c_btn, latch_btn) all as floats/bools
    """
    # Placeholder: Always return forward movement
    Keys = getch()
    if Keys == 'w':
        return (0.0, 1.0, False, False, False)
    elif Keys == 's':
        return (0.0, 0, False, False, False) # to be implemented as a U-turn and determine the movement.
    elif Keys == 'a':
        return (-1.0, 0.0, False, False, False)
    elif Keys == 'd':
        return (1.0, 0.0, False, False, False)
    elif Keys == 'e':
        return (0.0, 0.0, True, False, False)  # E-stop
    elif Keys == 'c':
        return (0.0, 0.0, False, True, False)  # Speed Cycle
    elif Keys == 'l':
        return (0.0, 0.0, False, False, True)  # Sit stand
    elif Keys == '':
        return (0.0, 0.0, False, False, False) # spacebar for terminate all
    elif Keys == 'x':
        print("Exiting...")
        sys.exit(0)
        
    else:
        return (0.0, -1.0, False, False, False)
    
    

#use for mocking
def getch():
    """Get a single key press (Windows)."""
    return msvcrt.getch().decode("utf-8").lower()

# Utility
VELOCITY_LEVELS = [0.3, 0.5, 0.8]
speed_idx = 1
VELOCITY = VELOCITY_LEVELS[speed_idx]
ROTATION = 0.6
e_stopped = False
standing = True


def map_direction(lx, ly, threshold=0.5):
    if ly < -threshold:
        return (VELOCITY, 0, 0)
    elif ly > threshold:
        return (-VELOCITY, 0, 0)
    elif lx < -threshold:
        return (0, VELOCITY, 0)
    elif lx > threshold:
        return (0, -VELOCITY, 0)
    return (0, 0, 0)


def Robot_movement(client, vx, vy, vr, duration=1.5):
    command = RobotCommandBuilder.synchro_velocity_command(vx, vy, vr)
    client.robot_command(command, end_time_secs=time.time() + duration)

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python spot_nunchuck_controller.py <ROBOT_IP>")
        return

    robot_ip = sys.argv[1]
    sdk = create_standard_sdk("SpotNunchuckClient")
    robot = sdk.create_robot(robot_ip)

    # Authenticate
    robot.authenticate("user", "qurrtsecso7z")  # Replace with real creds
    bosdyn.client.util.authenticate(robot)
    robot.time_sync.wait_for_sync()

    # Setup clients
    lease_client = robot.ensure_client(LeaseClient.default_service_name)
    command_client = robot.ensure_client(RobotCommandClient.default_service_name)

    lease = lease_client.take()
    lease_keep_alive = LeaseKeepAlive(lease_client)

    try:
        print("Powering on robot...")
        robot.power_on(timeout_sec=20)
        time.sleep(2)
        command_client.robot_command(RobotCommandBuilder.synchro_stand_command())
        time.sleep(2)

        global VELOCITY, speed_idx, e_stopped, standing
        last_cmd = (0, 0, 0)

        print("Controller active. Move joystick or press buttons.")

        while True:
            lx, ly, z_btn, c_btn, latch_btn = read_nunchuck()
            cmd = map_direction(lx, ly)
            Read = getch()
            if Read == 'X':
                exit(1)
            if cmd != last_cmd and cmd != (0, 0, 0):
                print(f"New command: {cmd}")
                Robot_movement(command_client, *cmd)
                last_cmd = cmd

            # Toggle E-stop
            if z_btn:
                if not e_stopped:
                    robot.command_client().estop()
                    print("E-STOP engaged!")
                    e_stopped = True
                else:
                    robot.power_on()
                    print("E-STOP released!")
                    e_stopped = False
                time.sleep(0.5)

            # Cycle speed
            if c_btn:
                speed_idx = (speed_idx + 1) % len(VELOCITY_LEVELS)
                VELOCITY = VELOCITY_LEVELS[speed_idx]
                print(f"Speed now: {VELOCITY} m/s")
                time.sleep(0.3)

            # Sit/Stand toggle
            if latch_btn:
                if standing:
                    print("Sitting down...")
                    command_client.robot_command(RobotCommandBuilder.synchro_sit_command())
                else:
                    print("Standing up...")
                    command_client.robot_command(RobotCommandBuilder.synchro_stand_command())
                standing = not standing
                time.sleep(0.4)

            time.sleep(0.1)

    finally:
        print("Stopping robot...")
        send_velocity(command_client, 0, 0, 0)
        lease_keep_alive.shutdown()
        lease_client.return_lease(lease)
        robot.power_off(cut_immediately=False)
        print("Robot powered off.")


def send_velocity(client, vx, vy, vr, duration=1.0):
    command = RobotCommandBuilder.synchro_velocity_command(vx, vy, vr)
    client.robot_command(command, end_time_secs=time.time() + duration)


if __name__ == '__main__':
    main()