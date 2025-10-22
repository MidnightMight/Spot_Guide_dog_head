from bosdyn.client import create_standard_sdk, ResponseError
from bosdyn.client.payload import PayloadClient, make_payload
from bosdyn.client.auth import AuthClient

# Replace these with your robot's details
ROBOT_IP = "192.168.80.3"
USERNAME = "user"
PASSWORD = "-----------PWD---------------"

def register_payload( GUID, Name_payload, DESC, Mount_name):
    sdk = create_standard_sdk('PayloadRegistrationClient')
    robot = sdk.create_robot(ROBOT_IP)
    robot.authenticate(USERNAME, PASSWORD)

    payload_client = robot.ensure_client(PayloadClient.default_service_name)

    # Define your payload
    payload = make_payload(
        name= Name_payload,
        description= DESC,
        guid=GUID,  # Must be unique for your payload
        version="1.0.0",
        is_authorized=True,
        is_enabled=True,
        mount_frame_name=Mount_name  # Rear port
    )

    try:
        response = payload_client.register_payload(payload)
        print("Payload registered:", response)
    except ResponseError as err:
        print("Failed to register payload:", err)

if __name__ == "__main__":
    register_payload('676c6ddc-336b-45de-9c77-ce7d4c8c251c','Pi and Head -Guidedog','Robotic Guide dog head project Consist of A RPI5, power, head assembly','MOUNT_FRAME_BODY_PAYLOAD' )
