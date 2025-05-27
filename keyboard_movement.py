import sys
import time
import numpy as np
import msvcrt
from bosdyn.client import create_standard_sdk
from bosdyn.client.lease import LeaseKeepAlive, LeaseClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient
import bosdyn.client.util

VELOCITY = 0.5  # m/s
ROTATION = 0.8  # rad/s
payload_exist = True

def getch():
    """Get a single key press (Windows)."""
    return msvcrt.getch().decode("utf-8").lower()

def getch_linux():
    """Get a single key press (Linux)."""
    import tty
    import termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch.lower()

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

def main():
    if len(sys.argv) != 2:
        print("Usage: python keyboard_movement.py <ROBOT_IP>")
        return

    robot_ip = sys.argv[1]
    sdk = create_standard_sdk("SpotKeyboardClient")
    robot = sdk.create_robot(robot_ip)

    # Authenticate and sync time
    robot.authenticate('user', 'qurrtsecso7z')  # Replace with your credentials
    bosdyn.client.util.authenticate(robot)
    robot.time_sync.wait_for_sync()

    # Setup clients
    lease_client = robot.ensure_client(LeaseClient.default_service_name)
    command_client = robot.ensure_client(RobotCommandClient.default_service_name)

    # Take lease and keep it alive
    lease = lease_client.take()
    lease_keep_alive = LeaseKeepAlive(lease_client)

    
    try:
        print("Powering on...")
        robot.power_on(timeout_sec=70)
        print("Standing up...")
        command_client.robot_command(RobotCommandBuilder.selfright_command())
        time.sleep(10)
        command_client.robot_command(RobotCommandBuilder.synchro_stand_command())
        time.sleep(2)

        print("\nControl Spot with:")
        print("  W/S = forward/backward")
        print("  A/D = strafe left/right")
        print("  Q/E = rotate left/right")
        print("  SPACE = stop")
        print("  X = exit\n")
        while True:
            key = getch()
            print(f"Key pressed: {key}")
            if key == 'w':
                Robot_movement(command_client, VELOCITY, 0, 0, head_movement=False)
            ##############################################################################
            # # Disabled due to the fact that the robot should not move backward
            # elif key == 's':
                # Robot_movement(command_client, -VELOCITY, 0, 0)
            elif key == 'a':
                print("Strafing left...")
                Robot_movement(command_client, 0, VELOCITY, 0)
            elif key == 'd':
                print("Strafing right...")
                Robot_movement(command_client, 0, -VELOCITY, 0)
            elif key == 'q':
                print("Rotating left...")
                Robot_movement(command_client, 0, 0, ROTATION)
            elif key == 'e':
                print("Rotating right...")
                Robot_movement(command_client, 0, 0, -ROTATION)
            elif key == 'j':
                print("Looking left...")
                send_velocity(command_client, 0, 0, 0)
                stand_look_around(command_client, yaw_deg=25)   # yaw left 30°
            elif key == 'l':
                print("Looking right...")
                send_velocity(command_client, 0, 0, 0)
                stand_look_around(command_client, yaw_deg=-25)  # yaw right 30°
            elif key == 'i':
                print("Look foward...")
                send_velocity(command_client, 0, 0, 0)
                stand_look_around(command_client, pitch_deg=5)    # yaw up 30°
            elif key == 'k':
                print("Looking down...")
                send_velocity(command_client, 0, 0, 0)
                stand_look_around(command_client, pitch_deg=-5)
            elif key == ' ':
                send_velocity(command_client, 0, 0, 0)
            elif key == 'b':
                command_client.robot_command(RobotCommandBuilder.battery_change_pose_command())
                time.sleep(10)
                break
            elif key == 'x':
                print("Exiting...")
                send_velocity(command_client, 0, 0, 0)
                break
            
            
    finally:
        # if no payload do this 
        if payload_exist == False:
            print("Battery accesible pose ? y/n")
            response = input().strip().lower()
            if response == 'y':
                print("Moving to battery accessible pose...")
                command_client.robot_command(RobotCommandBuilder.battery_change_pose_command())
                time.sleep(2)
                
            else:
                print("Sitting down pose.")
        print("Powering off...")
        robot.power_off(cut_immediately=False)
        lease_keep_alive.shutdown()
        lease_client.return_lease(lease)
        print("Done.")
    # Relaunch?
        


if __name__ == '__main__':
    main()
