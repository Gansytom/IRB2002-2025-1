#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import serial
import time
from std_msgs.msg import Float64

class MotorControllerNode(Node):
    def __init__(self):
        super().__init__("motor_controller_node")
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        self.ser.reset_input_buffer()

        # Create a suscriber for velocity
        self.vel_suscriber_ = self.create_subscription(
            Float64,
            "motion/cmd_vel",
            self.vel_callback,
            qos_profile=qos_profile_sensor_data
        )

    def vel_callback(self, msg):
        # Convert the velocity to a string and send it to the Arduino
        vel_str = str(msg.data) + "\n"
        self.ser.write(vel_str.encode('utf-8'))
        line = self.ser.readline().decode('utf-8').rstrip()
        self.get_logger().info(f"Velocity command: {line}")
        time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    node = MotorControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
