#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import serial
import time
from my_robot_interfaces.msg import CmdVel
import threading

class MotorDriverNode(Node):
    def __init__(self):
        super().__init__("motor_driver_node")
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        time.sleep(2)
        self.ser.reset_input_buffer()
        self.get_logger().info("Serial port opened successfully")
        # Lock for use ser
        self.lock = threading.Lock()
        self.switch = False
        self.vel_left = 0.0
        self.vel_right = 0.0
        # Check if the serial port is open
        if not self.ser.is_open:
            self.get_logger().error("Failed to open serial port")
            return

        # suscriber for velocity
        self.vel_suscriber_ = self.create_subscription(
            CmdVel,
            "motion/cmd_vel",
            self.cmd_vel_callback,
            qos_profile=qos_profile_sensor_data
        )

        self.create_timer(0.2, self.get_rpm_feedback)

        self.get_logger().info("Motor controller node started")  
    
    def cmd_vel_callback(self, msg):
        command = msg.command
        vel_left = msg.left_velocity
        vel_right = msg.right_velocity

        # Convert the velocity to a string and send it to the Arduino
        if command == "on" or command == "stop":
            cmd_str = command + "\n"
            self.switch = True if command == "on" else False
        else:
            cmd_str = f"{vel_left},{vel_right}\n"
            self.vel_left = vel_left
            self.vel_right = vel_right
        with self.lock:
            self.ser.write(cmd_str.encode('utf-8'))
            #self.get_rpm_feedback()
            #self.get_logger().info(f"Velocidades enviadas: {cmd_str.strip()}")
            self.ser.reset_input_buffer()

        #time.sleep(0.25)

    def get_rpm_feedback(self):
        # Read the RPM feedback from the Arduino
        self.lock.acquire()
        if self.ser.in_waiting > 0:
            # line = self.ser.readline().decode('utf-8',errors='ignore').rstrip()
            # self.get_logger().info(f"RPM feedback: {line}")
            raw_line = self.ser.readline()
            self.lock.release()
            try:
                line = raw_line.decode('utf-8', errors='ignore').rstrip()
                self.get_logger().info(f"RPM feedback: {line}")
                return line
            except UnicodeDecodeError as e:
                self.get_logger().error(f"Decode error: {e}")
                self.get_logger().error(f"Raw line (bytes): {raw_line}")
                # self.get_logger().error("Failed to decode RPM feedback. Raw data may not be UTF-8 encoded.")
                # # Log the raw line in hex and repr for debugging
                # self.get_logger().error(f"Raw line (hex): {raw_line.hex()}")
                # self.get_logger().error(f"Raw line (repr): {repr(raw_line)}")
        return None

def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
