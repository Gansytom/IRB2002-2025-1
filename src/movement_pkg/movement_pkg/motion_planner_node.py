#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
from my_robot_interfaces.msg import CmdVel
from my_robot_interfaces.srv import SetCmdVel


class MotionPlannerNode(Node):
    def __init__(self):
        super().__init__("motion_planner_node")

        # ----- Timers, publishers, suscribers and services -----
        self.vel_suscriber_ = self.create_subscription(
            CmdVel,
            "motion/cmd_vel",
            self.cmd_vel_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.set_vel_client_ = self.create_client(
            SetCmdVel, "set_vel")

        # ----- Parameters for command and velocities -----
        self.last_cmd_vel = CmdVel()
        self.last_cmd_vel.command = "stop"
        self.last_cmd_vel.left_velocity = 0.0
        self.last_cmd_vel.right_velocity = 0.0

    def cmd_vel_callback(self, msg): # Receive the command and velocities from the subscriber
        if self.last_cmd_vel.command != msg.command or \
           self.last_cmd_vel.left_velocity != msg.left_velocity or \
           self.last_cmd_vel.right_velocity != msg.right_velocity:
            cmd_vel = CmdVel()
            cmd_vel.command = msg.command
            cmd_vel.left_velocity = msg.left_velocity
            cmd_vel.right_velocity = msg.right_velocity
            self.call_set_vel(cmd_vel)
            self.last_cmd_vel = cmd_vel

    def call_set_vel(self, cmd_vel): # Call the service to set the velocities
        if not self.set_vel_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().error("Service not available, waiting...")
            return

        request = SetCmdVel.Request()
        request.command = cmd_vel.command
        request.left_velocity = cmd_vel.left_velocity
        request.right_velocity = cmd_vel.right_velocity

        future = self.set_vel_client_.call_async(request)
        future.add_done_callback(self.callback_call_set_vel)

    def callback_call_set_vel(self, future): # Callback for the service call
        response: SetCmdVel.Response = future.result()
        if response.success:
            self.get_logger().info("command sent successfully")
        else:
            self.get_logger().info("command failed to send")

def main(args=None):
    rclpy.init(args=args)
    node = MotionPlannerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
