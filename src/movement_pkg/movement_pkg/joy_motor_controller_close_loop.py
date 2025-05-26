#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
#import serial
import time
from geometry_msgs.msg import TwistStamped

class JoyMotorControllerNode(Node):
    def __init__(self):
        super().__init__("motor_controller_node")
        # self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
        # self.ser.reset_input_buffer()
        # self.get_logger().info("Serial port opened successfully")
        # Check if the serial port is open
        # if not self.ser.is_open:
        #     self.get_logger().error("Failed to open serial port")
        #     return

        # Create a suscriber for velocity
        self.vel_suscriber_ = self.create_subscription(
            TwistStamped,
            "motion/cmd_vel",
            self.cmd_vel_callback,
            qos_profile=qos_profile_sensor_data
        )

        self.get_logger().info("Motor controller node started")  

    def limit_velocity(self, vel):
        return max(-254, min(254, vel))
    
    def cmd_vel_callback(self, msg):
        # linear = msg.linear.x
        # angular = msg.angular.z

        # # Convert the linear and angular velocities to a single value
        # vel_izq = int(linear - angular)
        # vel_der = int(linear + angular)

        # # Limit the velocities to the range [-254, 254]
        # vel_izq = self.limit_velocity(vel_izq)
        # vel_der = self.limit_velocity(vel_der)

        # Convert the velocity to a string and send it to the Arduino
        # cmd_str = f"{vel_izq};{vel_der}\n"
        # self.ser.write(cmd_str.encode('utf-8'))
        command = msg.header.frame_id
        vel_left = int(msg.twist.linear.x)
        vel_right = int(msg.twist.linear.y)
        # Convert the velocity to a string and send it to the Arduino
        if command == "on" or command == "stop":
            cmd_str = command
        else:
            cmd_str = f"{vel_left},{vel_right}\n"
        # self.ser.write(cmd_str.encode('utf-8'))
        self.get_logger().info(f"Velocidades enviadas: {cmd_str.strip()}")


        time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    node = JoyMotorControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
