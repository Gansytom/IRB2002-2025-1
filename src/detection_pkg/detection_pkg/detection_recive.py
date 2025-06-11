#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
from yolo_msg.msg import Bottle, BottleArray
from geometry_msgs.msg import Point


class DetectionReciver(Node):
    def __init__(self):
        super().__init__("detection_recive")


        # Create a suscriber for images
        self.suscriber_ = self.create_subscription(
            BottleArray,
            "/bottle_detections",            
            self.callback,
            qos_profile=qos_profile_sensor_data
        )

    def callback(self, msg):
        number = msg.number
        if len(msg.bottles) != number:
            self.get_logger().info("ERROR")
        for bottle in msg.bottles:
            id = bottle.id
            conf = bottle.probability
            point = bottle.position
            self.get_logger().info(f"Bottle ID: {id}, conf: {conf}, point: ({point.x}, {point.y}) ")



def main(args=None):
    rclpy.init(args=args)
    node = DetectionReciver()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()