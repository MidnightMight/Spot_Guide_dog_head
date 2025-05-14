import bosdyn.client
# Removed unused import 'bosdyn.util'

# '''
# NAME
#     bosdyn.client

# DESCRIPTION
#     The client library package.
#     Sets up some convenience imports for commonly used classes.

# PACKAGE CONTENTS
#     __main__
#     area_callback
#     area_callback_region_handler_base
#     area_callback_service_runner
#     area_callback_service_servicer
#     area_callback_service_utils
#     arm_surface_contact
#     async_tasks
#     auth
#     auto_return
#     autowalk
#     bddf
#     bddf_download
#     channel
#     command_line
#     common
#     data_acquisition
#     data_acquisition_helpers
#     data_acquisition_plugin
#     data_acquisition_plugin_service
#     data_acquisition_store
#     data_buffer
#     data_chunk
#     data_service
#     directory
#     directory_registration
#     docking
#     door
#     estop
#     exceptions
#     fault
#     frame_helpers
#     gps (package)
#     graph_nav
#     gripper_camera_param
#     image
#     image_service_helpers
#     inverse_kinematics
#     ir_enable_disable
#     keepalive
#     lease
#     lease_resource_hierarchy
#     lease_validator
#     license
#     local_grid
#     log_status
#     manipulation_api_client
#     map_processing
#     math_helpers
#     metrics_logging
#     network_compute_bridge_client
#     payload
#     payload_registration
#     point_cloud
#     power
#     processors
#     ray_cast
#     recording
#     resources (package)
#     robot
#     robot_command
#     robot_id
#     robot_state
#     sdk
#     server_util
#     service_customization_helpers
#     signals_helpers
#     spot_cam (package)
#     spot_check
#     time_sync
#     token_cache
#     token_manager
#     units_helpers
#     util
#     world_object

# DATA
#     BOSDYN_RESOURCE_ROOT = r'C:\Users\buff1\.bosdyn'

# FILE
#     c:\users\buff1\miniconda3\envs\spot_bd\lib\site-packages\bosdyn\client\__init__.py
#     '''

# Prior to start 
# run this
# & C:/Users/buff1/miniconda3/envs/Spot_BD/python.exe "d:/Github - repo/Spot_Guide_dog_head/estop_gui.py" 192.168.80.3

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
        self.robot.authenticate('user', 'qurrtsecso7z') 

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
    """Command line interface."""
    robot = Leaser_system.create_robot(robot_ip='192.168.80.3')
    robot.authenticate('user', 'qurrtsecso7z')
    parser = argparse.ArgumentParser(description='Establishes an e-stop connection to a robot.')

    def run_estop():
        # Execute E-stop GUI script from the same folder
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'estop_gui.py'), '192.168.80.3'])
        # robot.authenticate('user', 'qurrtsecso7z')

    def run_wasd():
        # Start the WASD keyboard movement script
        
        subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), 'keyboard_movement.py'), '192.168.80.3'])
        # robot.authenticate('user', 'qurrtsecso7z')
        
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

    # Start threads
    estop_thread.start()
    print("Waiting for E-stop check-in...")
    wait_for_estop_start(logger)

    # Wait for the specific log message before starting the next thread
    

    # check if the threads are alive
    if estop_thread.is_alive():
        print("E-stop thread is running.")
        wasd_thread.start()
        while wasd_thread.is_alive():
            # Wait for the WASD thread to finish
            wasd_thread.join(timeout=1)
            
    else:
        print("E-stop thread is not running.")


    # Wait for threads to complete
    estop_thread.join()
    wasd_thread.join()
    

if __name__ == '__main__' and len(sys.argv) == 1:
    sys.argv.append('192.168.80.3')

if __name__ == '__main__':
    if not main():
        sys.exit(1)


print("script_ends !")


