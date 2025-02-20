#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")

        # Initialize the camera
        self.get_logger().info("Initializing camera...")
        self.bridge = CvBridge()
        self.cap = cv2.VideoCapture(0, cv2.CAP_V4L)
        self.cap.set(3, 640)
        self.cap.set(4, 640)
        if not self.cap.isOpened():
            raise ValueError("Could not open video device")
        ret, img = self.cap.read()
        if not ret or img is None:
            raise ValueError("Could not read image from video device")
        self.get_logger().info("Camera initialized successfully")

        # Create a publisher for images
        self.img_publisher_ = self.create_publisher(
            Image,
            "camera_topic",
            qos_profile=qos_profile_sensor_data
        )
        # Publish the image captured every 0.1 seconds
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.get_logger().info("Camera node started")

    def timer_callback(self):
        try:
            ret, img = self.cap.read()
            if not ret or img is None:
                self.get_logger().error("Failed to read image from camera")
                return
            
            # Publish a message
            msg = self.bridge.cv2_to_imgmsg(img, encoding="bgr8")
            self.img_publisher_.publish(msg)
            self.get_logger().info(f"Publishing image: {msg.header.stamp}")
        except CvBridgeError as e:
            self.get_logger().error(f"Error converting image: {e}")
            return


def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
