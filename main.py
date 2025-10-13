import bosdyn.client
import subprocess
from bosdyn.client import create_standard_sdk
from bosdyn.client.robot import Robot
import argparse
import os
import sys
import time

import bosdyn.client.lease
import bosdyn.client.util
import bosdyn.geometry
from bosdyn.api import trajectory_pb2
from bosdyn.api.spot import robot_command_pb2 as spot_command_pb2
from bosdyn.client import math_helpers
from bosdyn.client.frame_helpers import GRAV_ALIGNED_BODY_FRAME_NAME, ODOM_FRAME_NAME, get_a_tform_b
from bosdyn.client.image import ImageClient
from bosdyn.client.robot_command import RobotCommandBuilder, RobotCommandClient, blocking_stand
from bosdyn.client.robot_state import RobotStateClient
from bosdyn.util import seconds_to_duration
import hello_spot
from bosdyn.client.estop import EstopEndpoint, EstopClient
import threading
import logging
# Execute the ping command
if subprocess.run(["ping", "192.168.80.3"]):
    print("Ping successful")
else:
    print("Ping failed")
    exit(1)
                 
# Connect to the robot and check version
# Create SDK and robot instance
class Leaser_system:
    def create_robot(robot_ip: str):
        # Create a standard SDK instance
        sdk = create_standard_sdk('SpotClient')
        # Create a robot instance with the provided IP address
        robot = sdk.create_robot(robot_ip)
        return robot
    def __init__(self, robot: Robot):
        self.robot = robot
        self.lease_client = None

    def acquire_lease(self):
        # Acquire a lease on the robot
        self.lease_client = bosdyn.client.lease.LeaseClient(self.robot)
        self.lease_client.acquire_lease()

    def release_lease(self):
        # Release the lease on the robot
        if self.lease_client:
            self.lease_client.release_lease()
            self.lease_client = None

    def authentication(self):
        # Authenticate the robot
        self.robot.authenticate('user', 'qurrtsecso7z')  # Replace with your password before use.

class Basic_services:
    def get_pose(robot: Robot, frame_name: str):
        # Get the robot's pose in the specified frame
        robot_state_client = robot.ensure_client(RobotStateClient.default_service_name)
        robot_state = robot_state_client.get_robot_state()
        tform_body = get_a_tform_b(robot_state, frame_name, ODOM_FRAME_NAME)
        return tform_body
    
    def get_image(robot: Robot, camera_name: str):
        # Get an image from the specified camera
        image_client = robot.ensure_client(ImageClient.default_service_name)
        image_response = image_client.get_image(camera_name)
        return image_response
    
    


def main():
    IP_Address_main = '192.168.80.3'
    """Command line interface."""
    robot = Leaser_system.create_robot(robot_ip=IP_Address_main)
    robot.authenticate('user', 'qurrtsecso7z')
    parser = argparse.ArgumentParser(description='Establishes an e-stop connection to a robot.')

    def run_estop():
        # Execute E-stop GUI script from the same folder
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'estop_gui.py'), IP_Address_main])


    def run_wasd():
        # Start the WASD keyboard movement script
        
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'keyboard_movement.py'), IP_Address_main])

    def run_nunchuck():
        # Start the Nunchuck controller script
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'keyboard_xbox_movement.py'), IP_Address_main])
                            
    def run_xbox_v2():
        # Start the Xbox controller script
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'xbox_v2_movement.py'), IP_Address_main])
                        
    def wait_for_estop_start(logger: logging.Logger):
        """Wait for the E-stop check-in to start."""
        # import queue
        # print("Waiting for E-stop check-in...")
        # log_queue = queue.Queue()

        # class QueueHandler(logging.Handler):
        #     def emit(self, record):
        #         log_queue.put(self.format(record))

        # queue_handler = QueueHandler()
        # queue_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))
        # logger.addHandler(queue_handler)

        # try:
        #     while True:
        #         try:
        #             log_message = log_queue.get(timeout=1)  # Wait for log messages
        #             print(log_message)
        #             if 'INFO - Starting estop check-in' in log_message:
        #                 return
        #         except queue.Empty:
        #             continue
        # finally:
        #     logger.removeHandler(queue_handler)
        time.sleep(5)  # Wait for the E-stop check-in to start
        # code not working soo 7 seconds is best for now. 

    # Configure logging to capture the console output
    logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s', handlers=[logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger()

    # Create threads for E-stop and WASD
    estop_thread = threading.Thread(target=run_estop, daemon=True)
    wasd_thread = threading.Thread(target=run_wasd, daemon=True)

    # This thread is for the Xbox controller
    # X_box_thread = threading.Thread(target=run_xbox_v2, daemon=True)
    # camera_thread = threading.Thread(target=Basic_services.get_image, args=(robot, 'front_left_fisheye'), daemon=True)


    # Start threads
    estop_thread.start()
    print("Waiting for E-stop check-in...")
    wait_for_estop_start(logger)

    # Wait for the specific log message before starting the next thread
    

    # check if the threads are alive
    if estop_thread.is_alive():
        print("E-stop thread is running.")
        wasd_thread.start()

        print("WASD thread started.")
        # Start the Xbox controller thread
        # X_box_thread.start()
        # print("Xbox controller thread started.")
        # Start the camera thread
        # camera_thread.start()
        # print("Camera thread started.")

        while wasd_thread.is_alive():
            # Wait for the WASD thread to finish
            wasd_thread.join(timeout=1)
            
    else:
        print("E-stop thread is not running.")


    # Wait for threads to complete
    estop_thread.join()
    wasd_thread.join()

    # Threads for Xbox controller and camera can be started similarly
    # X_box_thread.join()
    # camera_thread.join()
    

if __name__ == '__main__' and len(sys.argv) == 1:
    sys.argv.append('192.168.80.3')

if __name__ == '__main__':
    if not main():
        sys.exit(1)


print("script_ends !")


