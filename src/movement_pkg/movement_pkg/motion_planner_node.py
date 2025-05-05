#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64


class MotionPlannerNode(Node):
    def __init__(self):
        super().__init__("motion_planner_node")
        self.get_logger().info("Motion Planner Node has been started.")
        # Create a timer to periodically call the planner function
        self.vel_timer = self.create_timer(0.1, self.vel_timer_cb)
        # Create a publisher for the velocity command
        self.publisher_ = self.create_publisher(Float64, "motion/cmd_vel", 10)

    def vel_timer_cb(self):
        # Create a new message
        msg = Float64()
        # Set the velocity value
        msg.data = 100.0
        # Publish the message
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = MotionPlannerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
