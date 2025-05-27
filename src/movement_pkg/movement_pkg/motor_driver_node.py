#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import serial
import time
from my_robot_interfaces.msg import CmdVel

class MotorDriverNode(Node):
    def __init__(self):
        super().__init__("motor_driver_node")
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.ser.reset_input_buffer()
        self.get_logger().info("Serial port opened successfully")
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

        self.get_logger().info("Motor controller node started")  
    
    def cmd_vel_callback(self, msg):
        command = msg.command
        vel_left = msg.left_velocity
        vel_right = msg.right_velocity

        # Convert the velocity to a string and send it to the Arduino
        if command == "on" or command == "stop":
            cmd_str = command
        else:
            cmd_str = f"{vel_left},{vel_right}\n"
        self.ser.write(cmd_str.encode('utf-8'))
        self.get_logger().info(f"Velocidades enviadas: {cmd_str.strip()}")

        #time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
