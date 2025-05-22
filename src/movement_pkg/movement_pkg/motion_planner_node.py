#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
import threading


class MotionPlannerNode(Node):
    def __init__(self):
        super().__init__("motion_planner_node")
        self.get_logger().info("Motion Planner Node has been started.")
        # Create a timer to periodically call the planner function
        # self.vel_timer = self.create_timer(0.1, self.vel_timer_cb)
        # Create a publisher for the velocity command
        self.publisher_ = self.create_publisher(TwistStamped, "motion/cmd_vel", 10)

        # Ejecutar input por consola en hilo aparte para no bloquear ROS
        self.input_thread = threading.Thread(target=self.read_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    # def vel_timer_cb(self):
    #     # Create a new message
    #     msg = Twist()
    #     # Set the velocity value
    #     msg.data = 100.0
    #     # Publish the message
    #     self.publisher_.publish(msg)
    #     self.get_logger().info(f"Publishing: {msg.data}")

    def read_input_loop(self):
        while rclpy.ok():
            line = input("Ingresa alguno de los siguientes comandos:\n- on\n- stop\n- <vel_motor_izquierdo> <vel_motor_derecho>\n")
            parts = line.strip().split()
            if str(line) != "on" or str(line) != "stop" or len(parts) != 2:
                self.get_logger().warn("Comando incorrecto.")
                continue

            msg = TwistStamped()
            if str(line) == "on":
                self.get_logger().info("Encendiendo motores...")
                msg.header.frame_id = "on"
                msg.twist.linear.x = 0.0
                msg.twist.linear.y = 0.0
            elif str(line) == "stop":
                self.get_logger().info("Deteniendo motores...")
                msg.header.frame_id = "stop"
                msg.twist.linear.x = 0.0
                msg.twist.linear.y = 0.0
            else:
                msg.header.frame_id = "-"
                vel_left = float(parts[0])
                vel_right = float(parts[1])
                
                msg.twist.linear.x = vel_left
                msg.twist.linear.y = vel_right
                #msg.twist.angular.z = vel_rotacion

            self.publisher_.publish(msg)
            self.get_logger().info(f"Publicando: {msg.twist.linear.x}, {msg.twist.linear.y}")
            # Esperar un segundo antes de continuar
            # time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    node = MotionPlannerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
