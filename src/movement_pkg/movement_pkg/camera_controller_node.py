#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
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
        self.cmd_publisher = self.create_publisher(CmdVel, "motion/cmd_vel", 10)
        # ----- Parameters -----
        self.state = None
        self.y_distance_factor = 0.7
        self.x_distance_factor = 1 - self.y_distance_factor

        self.pid = PID(kp=0.05, ki=0.0, kd=0.001)
        self.last_time = self.get_clock().now().nanoseconds / 1e9
        self.target = None
        self.base_speed = 45 # 75 o 45
        self.shovel_base_speed = 150.0

        self.tracked_target = None
        self.tracking_counter = 0
        self.tracking_max_lost = 20
        self.tracking_lost_counter = 0
        self.tracking_confirm_threshold = 5
        self.last_detection = None

        # ----- Axis criteria -----
        self.above_distance_factor = 0.6
        self.below_distance_factor = 1.4
        self.shovel_distance_factor = 1.7
        self.align_threshold = 200
        self.axis_criteria = None

        # ----- Shovel activation control -----
        self.shovel_sent = False
        self.shovel_start_time = None
        self.shovel_wait_time = 1.5  # seconds

    def prediction_callback(self, msg): # Callback for the prediction subscriber
        if not msg.bottles:
            self.tracking_lost_counter += 1
            if self.tracking_lost_counter > self.tracking_max_lost:
                self.tracked_target = None
                self.tracking_counter = 0
                self.shovel_sent = False
                self.shovel_start_time = None
                cmd = CmdVel()
                cmd.command = "move"
                cmd.left_velocity = 0.0
                cmd.right_velocity = 0.0
                self.cmd_publisher.publish(cmd)
            return

        # Choose the bottle with min distance to the bottom of the image and min distance to the center
        candidate = min(msg.bottles, key=lambda 
                        b: self.y_distance_factor*(b.img_height - b.y) 
                        + self.x_distance_factor*abs(b.x - (b.img_width // 2))
        )

        if self.tracked_target is None:
            if self.last_detection is not None and self.is_near(candidate, self.last_detection, threshold=40):
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
        
        img_center_x = target.img_width // 2
        img_center_y = target.img_height // 2
        error = target.x - img_center_x

        now = self.get_clock().now().nanoseconds / 1e9
        dt = now - self.last_time
        self.last_time = now

        correction = self.pid.compute(error, dt)

        # Set the state based on the target position
        is_aligned = abs(target.x - img_center_x) < self.align_threshold
        is_far = target.y < img_center_y * self.above_distance_factor
        is_close = target.y > img_center_y * self.below_distance_factor
        is_middle = not is_far and not is_close
        is_shovel_ready = target.y > img_center_y * self.shovel_distance_factor

        # ----- State machine logic (first version)-----

        if not is_close:
            self.state = "align_forward"
        elif is_close and not is_aligned:
            self.state = "align_backward"
        elif is_close and is_aligned:
            self.state = "use_shovel"

        if self.state != "use_shovel":
            self.shovel_sent = False
            self.shovel_start_time = None

        # ----- State machine logic (second version)-----
        # if is_far or (is_middle and self.state == "align_forward"):
        #     self.state = "align_forward"
        # elif is_close or (is_middle and self.state == "align_backward"):
        #     self.state = "align_backward"
        # elif is_middle and self.state == "use_shovel":
        #     self.state = "align_forward"

        # if is_shovel_ready and is_aligned:
        #     self.state = "use_shovel"
        # elif is_close and is_aligned:
        #     self.state = "align_forward"

        # if self.state != "use_shovel":
        #     self.shovel_sent = False
        #     self.shovel_start_time = None

        # Set the command based on the state
        cmd = CmdVel()
        if self.state == "align_forward":
            cmd.command = "move"
            cmd.left_velocity = self.base_speed + correction
            cmd.right_velocity = self.base_speed - correction
        elif self.state == "align_backward":
            cmd.command = "move"
            cmd.left_velocity = -(self.base_speed - correction)
            cmd.right_velocity = -(self.base_speed + correction)
        elif self.state == "use_shovel":
            if not self.shovel_sent:
                if self.shovel_start_time is None:
                    self.shovel_start_time = now
                    
                elif now - self.shovel_start_time > self.shovel_wait_time:
                    self.get_logger().info("Shovel command issued.")
                    cmd.command = "shovel"
                    cmd.left_velocity = self.shovel_base_speed
                    cmd.right_velocity = self.shovel_base_speed
                    self.shovel_sent = True

        self.cmd_publisher.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = CameraControllerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
