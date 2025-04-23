#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from example_interfaces.msg import String
import cv2


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")

        # Initialize the camera
        self.get_logger().info("Initializing camera...")
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            raise ValueError("Could not open video device")
        ret, img = self.vid.read()
        if not ret or img is None:
            raise ValueError("Could not read image from video device")
        self.get_logger().info("Camera initialized successfully")
        
        self.create_publisher(
            String,
            "camera_topic",
            10
        )
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info("Camera node started")

    def timer_callback(self):
        ret, img = self.vid.read()
        if not ret or img is None:
            self.get_logger().error("Failed to read image from camera")
            return

        # Process the image (for example, convert to grayscale)
        #gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Display the image
        cv2.imshow("Camera Feed", img)
        cv2.waitKey(1)

        # Publish a message
        msg = String()
        msg.data = "Image captured"
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
