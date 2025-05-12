#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import threading


class MotionPlannerNode(Node):
    def __init__(self):
        super().__init__("motion_planner_node")
        self.get_logger().info("Motion Planner Node has been started.")
        # Create a timer to periodically call the planner function
        # self.vel_timer = self.create_timer(0.1, self.vel_timer_cb)
        # Create a publisher for the velocity command
        self.publisher_ = self.create_publisher(Twist, "motion/cmd_vel", 10)

        # Ejecutar input por consola en hilo aparte para no bloquear ROS
        self.input_thread = threading.Thread(target=self.read_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def vel_timer_cb(self):
        # Create a new message
        msg = Twist()
        # Set the velocity value
        msg.data = 100.0
        # Publish the message
        self.publisher_.publish(msg)
        self.get_logger().info(f"Publishing: {msg.data}")

    def read_input_loop(self):
        while rclpy.ok():
            try:
                line = input("Ingresa: <vel_avance> <vel_rotacion> <tiempo>\nEjemplo: 100.0 20.0 5.0\n> ")
                parts = line.strip().split()
                if len(parts) != 3:
                    self.get_logger().warn("Formato incorrecto. Se esperaban 3 valores.")
                    continue

                vel_avance = float(parts[0])
                vel_rotacion = float(parts[1])
                duracion = float(parts[2])

                msg = Twist()
                msg.linear.x = vel_avance
                msg.angular.z = vel_rotacion
                msg.angular.x = duracion

                self.publisher_.publish(msg)
                self.get_logger().info(f"Publicado: avance={vel_avance}, rotación={vel_rotacion}, duración={duracion}s")

            except ValueError:
                self.get_logger().warn("Entrada inválida. Usa números reales separados por espacios.")


def main(args=None):
    rclpy.init(args=args)
    node = MotionPlannerNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
