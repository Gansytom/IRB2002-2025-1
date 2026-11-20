# R 3/4 – Autonomous Beach-Cleaning Robot

Capstone project for **IRB2002 – Robotic Systems Design** (Pontificia Universidad Católica de
Chile, 2025-1). A differential-drive mobile robot that detects plastic bottles on sand with a
camera, drives to them and picks them up with a motorized shovel.

## How it works

```
 camera ──► YOLO detector ──► visual servo controller ──► motion planner ──► motor driver ──► Arduino
 (camera_cpp)  (detection_pkg)    (camera_controller_node)    (service call)     (serial)     (PID + shovel)
```

1. **Perception** – a camera node (C++, OpenCV/V4L2) publishes images. A YOLO11 model
   trained to detect bottles (`yolov11_node`, with NCNN exports for embedded inference) publishes the
   detected bottles as a custom `BottleArray` message (position and size in the image).
2. **Target selection and tracking** – the controller picks the bottle closest to the robot
   (bottom-center of the image), confirms it over several frames and keeps tracking it so it
   doesn't jump between detections.
3. **Visual servoing** – a state machine (`align_forward` → `align_backward` → `use_shovel`) with
   a PID on the horizontal pixel error steers the robot towards the bottle. Once the bottle has
   been close and centered for 2 s, the shovel command is sent.
4. **Low level** – the motion planner forwards commands only when they change, through a ROS 2
   service, to the motor driver, which talks to the Arduino over serial with a retry/ack
   mechanism. The Arduino runs a closed-loop PID speed controller per wheel (encoder feedback,
   ramped references) and a state machine for the shovel with end-stop switches.

Localization experiments (differential GPS with two receivers and an EKF via
`robot_localization`) are in `software/location` and `my_robot_bringup/config/ekf.yaml`.

## Repository layout

| Path | Contents |
|---|---|
| `src/camera_cpp_pkg` | C++ camera publisher (OpenCV, `image_transport`). |
| `src/detection_pkg` | YOLO detection nodes (YOLOv8 / YOLO11, PyTorch and NCNN models). |
| `src/movement_pkg` | Visual servo controller, motion planner, serial motor driver, joystick/terminal teleop. |
| `src/my_robot_interfaces` | Custom messages (`Bottle`, `BottleArray`, `CmdVel`) and service (`SetCmdVel`). |
| `src/my_robot_bringup` | Launch files and EKF configuration. |
| `software/control/arduino` | Arduino firmware: wheel PID control, shovel, communication tests. |
| `software/location` | Differential GPS firmware and localization scripts. |
| `software/communication` | Raspberry Pi ↔ Arduino serial tests. |

## Running

Built with ROS 2 Humble and `colcon`:

```bash
colcon build --symlink-install
source install/setup.bash

# Autonomous bottle collection (one terminal each)
ros2 launch my_robot_bringup camera_integration.launch.xml   # C++ camera + visual servo controller
ros2 run detection_pkg yolov11_node                          # YOLO11 bottle detector
ros2 launch my_robot_bringup motion_communication.launch.xml # motion planner + Arduino driver

# Manual control with a joystick
ros2 launch my_robot_bringup joy_close_loop.launch.xml
```

Python dependencies: `ultralytics`, `opencv-python`, `pyserial`. The Arduino is expected on
`/dev/ttyACM0`, and the YOLO model path is set inside `detection_pkg/yolov11_node.py`.

## Team

Developed by Group 1 of IRB2002 (2025-1). Navigation, control and perception by
[Tomás López](https://github.com/Gansytom), with contributions from
[FernandoTFH](https://github.com/FernandoTFH) and the rest of the team.
