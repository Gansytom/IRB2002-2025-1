#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import serial
import time
from my_robot_interfaces.msg import CmdVel
from my_robot_interfaces.srv import SetCmdVel
import threading

class MotorDriverNode(Node):
    def __init__(self):
        super().__init__("motor_driver_node")

        # ----- Initialize the serial port -----
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(1)
        self.ser.reset_input_buffer()
        self.get_logger().info("Serial port opened successfully")
        if not self.ser.is_open:
            self.get_logger().error("Failed to open serial port")
            return

        # ----- Timers, publishers, suscribers and services -----
        self.set_led_service_ = self.create_service(
            SetCmdVel, "set_vel", self.callback_set_vel)
        self.rpm_feedback_timer = self.create_timer(
           0.2, self.get_rpm_feedback)
        self.get_logger().info("Motor driver node started")

        # ----- Parameters -----
        self.lock = threading.Lock()

    def callback_set_vel(self, request: SetCmdVel.Request, response: SetCmdVel.Response): # Callback for the service to set the velocities
        with self.lock:
            command = request.command
            vel_left = request.left_velocity
            vel_right = request.right_velocity
            self.send_to_arduino(command, vel_left, vel_right)
        response.success = True
        response.message = f"Command '{command}' with velocities ({vel_left}, {vel_right}) sent to Arduino."
        return response

    def send_to_arduino(self, command, vel_left, vel_right): # Convert the velocity to a string and send it to the Arduino
        if command == "on" or command == "stop":
            cmd_str = command + "\n"
        else:
            cmd_str = f"{command},{vel_left},{vel_right}\n"
        self.ser.write(cmd_str.encode('utf-8'))
        self.ser.reset_input_buffer()
        self.get_logger().info(f"Sending command to Arduino: {cmd_str.strip()}")

        time.sleep(0.1)

    def get_rpm_feedback(self): # Read the RPM feedback from the Arduino
        if self.ser.in_waiting > 0:
            with self.lock:
                raw_line = self.ser.readline()
                line = raw_line.decode('utf-8', errors='ignore').rstrip()
                self.get_logger().info(f"RPM feedback: {line}")
                return line
        return None

def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
