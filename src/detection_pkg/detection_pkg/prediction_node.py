#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import cv2
from sensor_msgs.msg import Image
from cv_bridge import CvBridge, CvBridgeError


class PredictionNode(Node):
    def __init__(self):
        super().__init__("prediction_node")
        self.bridge = CvBridge()

        # Create a suscriber for images
        self.img_suscriber_ = self.create_subscription(
            Image,
            "camera_topic",
            self.img_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.get_logger().info("Prediction node started")

    def img_callback(self, msg):
        try:
            # Convert the ROS Image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
            cv2.imshow("Prediction Capture", cv_image)
            cv2.waitKey(1)
        except CvBridgeError as e:
            self.get_logger().error(f"Error converting image: {e}")
            return

def main(args=None):
    rclpy.init(args=args)
    node = PredictionNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
