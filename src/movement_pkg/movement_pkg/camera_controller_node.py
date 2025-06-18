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
        self.pid = PID(kp=0.05, ki=0.0, kd=0.001)
        self.last_time = self.get_clock().now().nanoseconds / 1e9
        self.target = None
        self.base_speed = 40
        self.align_threshold = 15

        self.tracked_target = None
        self.tracking_counter = 0
        self.tracking_max_lost = 10
        self.tracking_lost_counter = 0
        self.tracking_confirm_threshold = 5
        self.last_detection = None

    def prediction_callback(self, msg): # Callback for the prediction subscriber
        if not msg.bottles:
            self.tracking_lost_counter += 1
            if self.tracking_lost_counter > self.tracking_max_lost:
                self.tracked_target = None
                self.tracking_counter = 0
            return

        # Choose the bottle with the largest area as the candidate
        candidate = max(msg.bottles, key=lambda b: b.width * b.height)
        
        if self.tracked_target is None:
            if self.last_detection and self.is_near(candidate, self.last_detection, threshold=40):
                self.tracking_counter += 1
            else:
                self.tracking_counter = 1
            self.last_detection = candidate

            if self.tracking_counter >= self.tracking_confirm_threshold:
                self.tracked_target = candidate
                self.tracking_lost_counter = 0
                self.process_results(candidate)
        else:
            closest = min(msg.bottles, key=lambda b: self.distance(b, self.tracked_target))
            if self.is_near(closest, self.tracked_target, threshold=60):
                self.tracked_target = closest
                self.tracking_lost_counter = 0
                self.process_results(closest)
            else:
                self.tracking_lost_counter += 1
                if self.tracking_lost_counter > self.tracking_max_lost:
                    self.tracked_target = None
                    self.tracking_counter = 0
        
    def distance(self, a, b):
        return np.hypot(a.x - b.x, a.y - b.y)

    def is_near(self, a, b, threshold=40):
        return self.distance(a, b) < threshold

    def process_results(self, target): # Process the results from the prediction
        self.get_logger().info(f"Tracking target: {target.id} at ({target.x}, {target.y}) with area {target.width * target.height}")
        
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


def main(args=None):
    rclpy.init(args=args)
    node = CameraControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
