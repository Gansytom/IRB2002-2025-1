#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
import cv2
import numpy as np
from my_robot_interfaces.msg import CmdVel, BottleArray


class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.prev_error = 0
        self.integral = 0

    def compute(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev_error) / dt if dt > 0 else 0
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.prev_error = error
        return output
    
class CameraControllerNode(Node):
    def __init__(self):
        super().__init__("camera_controller_node")
        # ----- Timers, publishers, suscribers and services -----
        self.prediction_subscriber = self.create_subscription(
            BottleArray,
            "bottle_detections",
            self.prediction_callback,
            qos_profile_sensor_data
        )
        self.publisher = self.create_publisher(CmdVel, "motion/cmd_vel", 10)
        # ----- Parameters -----
        #self.cap = cv2.VideoCapture(1, cv2.CAP_V4L)
        self.pid = PID(kp=0.05, ki=0.0, kd=0.001)
        self.last_time = self.get_clock().now().nanoseconds / 1e9
        self.target = None
        #cv2.namedWindow("Camera")
        #cv2.setMouseCallback("Camera", self.mouse_callback)

        #self.timer = self.create_timer(0.1, self.timer_callback)
        #self.get_logger().info("Camera node started")
        self.base_speed = 40
        self.align_threshold = 15  # Threshold for alignment correction

    # def timer_callback(self):
    #     # ret, img = self.cap.read()
    #     # if not ret or img is None:
    #     #     self.get_logger().error("Failed to read image from camera")
    #     #     return

    #     # Lee la imagen desde archivo
    #     img = cv2.imread("/home/tomy/IRB2002-2025-1/src/movement_pkg/movement_pkg/arena_v1_00799.jpg")
    #     if img is None:
    #         self.get_logger().error("No se pudo leer la imagen arena_v1_00799.jpg")
    #         return
    #     cv_image = cv2.resize(img, (640, 480))
    #     self.process_results(self.target, cv_image)

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.target = (x, y)
            self.get_logger().info(f"Nuevo target seleccionado: {self.target}")

    def prediction_callback(self, msg):
        for prediction in msg.bottles:
            self.process_results(prediction)

    def process_results(self, target):
        # if self.target is None:
        #     cv2.imshow("Camera", cv_image)
        #     cv2.waitKey(1)
        #     return

        img_center_x = target.width // 2
        img_center_y = target.height // 2
        error = target.x - img_center_x

        now = self.get_clock().now().nanoseconds / 1e9
        dt = now - self.last_time
        self.last_time = now

        correction = self.pid.compute(error, dt)


        if target.y < img_center_y or \
            target.x > img_center_x - self.align_threshold and \
            target.x < img_center_x + self.align_threshold:

            left_vel = self.base_speed + correction
            right_vel = self.base_speed - correction
        else:
            left_vel = -(self.base_speed - correction)
            right_vel = -(self.base_speed + correction)

        cmd = CmdVel()
        cmd.command = "move"
        cmd.left_velocity = float(left_vel)
        cmd.right_velocity = float(right_vel)
        self.publisher.publish(cmd)

        # cv2.circle(cv_image, self.target, 5, (0, 0, 255), -1)
        # cv2.line(cv_image, (self.img_center_x, 0), (self.img_center_x, cv_image.shape[0]), (255, 0, 0), 2)
        # cv2.line(cv_image, (0, self.img_center_y), (cv_image.shape[1], self.img_center_y), (0, 255, 0), 2)
        # cv2.imshow("Camera", cv_image)
        # cv2.waitKey(1)


def main(args=None):
    rclpy.init(args=args)
    node = CameraControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
