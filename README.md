# Spot Guide Dog Head

A robotics project developed as part of a thesis at QUT (Queensland University of Technology) for the QCR (Queensland Centre for Robotics). The project attaches a custom animatronic guide-dog head to a Boston Dynamics Spot robot, allowing it to communicate heading cues to a visually-impaired handler via head articulation while being driven remotely over UDP.

**Demo video:** https://youtu.be/b5a-Ekf3FTs

---

## Table of Contents

- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Hardware Requirements](#hardware-requirements)
- [Software Dependencies](#software-dependencies)
- [Setup & Installation](#setup--installation)
- [Usage](#usage)
  - [Trial Run (head articulation only)](#trial-run-head-articulation-only)
  - [Spot SDK Control (laptop)](#spot-sdk-control-laptop)
  - [Raspberry Pi UDP Head Controller](#raspberry-pi-udp-head-controller)
- [Configuration](#configuration)
- [Known Limitations](#known-limitations)

---

## Project Overview

The system consists of three main layers:

1. **Operator laptop** – sends directional commands (WASD / Xbox / nunchuck) to Spot and simultaneously relays movement intent to the Raspberry Pi over UDP.
2. **Raspberry Pi 5 (on-board payload)** – receives UDP commands and drives three hobby servos (pan, tilt, handle-tilt) via a PCA9685 I²C PWM driver to articulate the guide-dog head.
3. **Boston Dynamics Spot** – locomotion is commanded directly through the Spot SDK; the Pi payload is registered as an authorised payload on the robot.

---

## Repository Structure

```
Spot_Guide_dog_head/
├── README.md                        # This file
├── payload_rego.py                  # Payload registration helper (root copy)
│
├── Trial_run_script/                # First working trial — head articulation + UDP
│   ├── Client_script.py             # Laptop-side UDP client (sends commands to Pi)
│   ├── UDP_Client_control.py        # Pi-side UDP server + servo execution (v2.1)
│   ├── Serial_to_GPIO_v2.py         # Servo initialisation & calibration routines
│   └── setup_text.txt               # Brief setup notes
│
├── Pi-Code/                         # Raspberry Pi code experiments
│   ├── Basic_servo.py               # Minimal PCA9685 PWM test
│   ├── Head_movement.py             # IK-based head movement prototype
│   ├── Server_UDP.py                # Standalone UDP relay server
│   └── UDP_Head_movement/           # Integrated UDP + servo controller
│       ├── Pi_main_script.py        # Main entry point for the Pi (UDP + Spot SDK stubs)
│       ├── Serial_to_GPIO.py        # Servo interface & smooth-motion helpers
│       └── Spot_functions.py        # Spot SDK velocity / stand commands (Pi version)
│
└── Spot_sdk_attempt/                # Laptop-side Spot SDK scripts
    ├── main.py                      # Orchestrator: launches e-stop + movement threads
    ├── hello_spot.py                # Boston Dynamics "Hello Spot" tutorial example
    ├── keyboard_movement.py         # WASD keyboard control of Spot
    ├── keyboard_xbox_movement.py    # Nunchuck / simulated-joystick control
    ├── estop_gui.py                 # PyQt5 software E-Stop GUI
    ├── payload_rego.py              # Registers the Pi payload with Spot
    ├── shutdown.py                  # Graceful shutdown helper
    └── xbox_controller/             # Third-party Xbox controller library
        ├── README.md                # Xbox controller usage guide
        ├── requirements.txt         # Controller library requirements
        ├── xbox_controller.py
        ├── xbox_joystick.py
        ├── xbox_joystick_factory.py
        ├── xbox_joystick_linux.py
        └── xbox_joystick_windows.py
```

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Boston Dynamics Spot | Any generation with Spot SDK support |
| Raspberry Pi 5 | Mounted as a payload on Spot's back |
| PCA9685 PWM driver | Connected to the Pi via I²C (SDA/SCL) |
| Hobby servo × 3 | Pan (servo 0), tilt (servo 1), handle-tilt (servo 2) |
| Guide-dog head assembly | 3-D printed / physical head attached to servos |
| Laptop / control PC | Windows or Linux; runs Spot SDK + sends UDP commands |

---

## Software Dependencies

### Raspberry Pi

```bash
pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-servokit numpy
```

### Laptop (Spot SDK side)

```bash
pip install bosdyn-client bosdyn-mission bosdyn-choreography-client numpy
# For the e-stop GUI:
pip install PyQt5
# For Xbox controller support (see Spot_sdk_attempt/xbox_controller/requirements.txt):
pip install -r Spot_sdk_attempt/xbox_controller/requirements.txt
```

---

## Setup & Installation

### 1. Authenticate credentials

All scripts that connect to Spot use a username/password pair. Search for `InsertPasswordHere` in the codebase and replace it with your robot's actual credentials **before running any script**. Never commit real credentials to version control.

Files that contain the placeholder:
- `Spot_sdk_attempt/keyboard_movement.py`
- `Spot_sdk_attempt/keyboard_xbox_movement.py`
- `Spot_sdk_attempt/estop_gui.py`
- `Spot_sdk_attempt/payload_rego.py`
- `Spot_sdk_attempt/main.py`
- `payload_rego.py`

### 2. Set Spot's IP address

Default IP used throughout the code is `192.168.80.3` (Spot's LAN address) and `192.168.80.102` (Pi payload address). Update these constants to match your network configuration.

### 3. Register the payload (first time only)

```bash
python Spot_sdk_attempt/payload_rego.py
```

This registers the Raspberry Pi + head assembly as an authorised payload on Spot.

---

## Usage

### Trial Run (head articulation only)

This is the most recent and fully-tested path. It does **not** require the Spot SDK.

**On the Raspberry Pi:**
```bash
python Trial_run_script/UDP_Client_control.py
```
The Pi binds to `192.168.80.102:5005` and waits for single-character commands from the laptop.

**On the laptop:**
```bash
python Trial_run_script/Client_script.py
```
Enter a nickname when prompted, then type single-character commands:

| Key | Head movement |
|-----|--------------|
| `w` | Look up |
| `x` | Look down |
| `a` | Look left |
| `d` | Look right |
| `q` | Look up-left |
| `e` | Look up-right |
| `z` | Look down-left |
| `c` | Look down-right |
| `s` | Centre (default position) |

---

### Spot SDK Control (laptop)

> **Note:** The Spot SDK scripts were developed and tested but were not used in the final trial because a live camera feed was required for safe teleoperation; Spot's original controller was used instead.

**Start the orchestrator (e-stop + WASD threads):**
```bash
python Spot_sdk_attempt/main.py
```
This automatically connects to `192.168.80.3`, launches the PyQt5 E-Stop GUI in a background thread, and then starts the WASD keyboard controller.

**Run the WASD controller standalone:**
```bash
python Spot_sdk_attempt/keyboard_movement.py <ROBOT_IP>
```

| Key | Action |
|-----|--------|
| `W` | Move forward |
| `A` | Strafe left |
| `D` | Strafe right |
| `Q` | Rotate left |
| `E` | Rotate right |
| `J` | Look left (body yaw) |
| `L` | Look right (body yaw) |
| `I` | Look forward (body pitch up) |
| `K` | Look down (body pitch down) |
| `SPACE` | Stop |
| `B` | Battery-change pose then exit |
| `X` | Exit |

**Run the E-Stop GUI standalone:**
```bash
python Spot_sdk_attempt/estop_gui.py <ROBOT_IP>
```

---

### Raspberry Pi UDP Head Controller

For a more integrated setup (UDP + Spot SDK stubs):

```bash
python Pi-Code/UDP_Head_movement/Pi_main_script.py
```

The script binds a UDP socket on the Pi's local IP at port `5005`, spawns a command-receiving thread, and delegates movement to `Serial_to_GPIO.py`.

---

## Configuration

| Constant | File | Default | Description |
|----------|------|---------|-------------|
| `SERVER_IP` | `Trial_run_script/UDP_Client_control.py` | `192.168.80.102` | Pi IP address |
| `SERVER_PORT` | Multiple | `5005` | UDP port |
| `VELOCITY` | `Spot_sdk_attempt/keyboard_movement.py` | `0.5` m/s | Spot walk speed |
| `ROTATION` | `Spot_sdk_attempt/keyboard_movement.py` | `0.8` rad/s | Spot rotation speed |
| `VELOCITY_LEVELS` | `Spot_sdk_attempt/keyboard_xbox_movement.py` | `[0.3, 0.5, 0.8]` | Speed presets |
| Servo default angles | `Trial_run_script/UDP_Client_control.py` | `(110, 85, 90)` | Pan, tilt, handle-tilt |

---

## Known Limitations

- The Spot SDK movement scripts import `msvcrt` (Windows-only). On Linux, use `getch_linux()` defined in `keyboard_movement.py` instead of `getch()`.
- Live camera feed integration was not completed in time for the trial; Spot's original tablet controller was used for navigation.
- The `Pi-Code/UDP_Head_movement/Spot_functions.py` file contains both servo helpers and Spot SDK stubs in a single file and is intended as a reference/prototype rather than production code.
- `Spot_sdk_attempt/main.py` hardcodes `192.168.80.3` as the robot IP. Update `IP_Address_main` to match your deployment.
