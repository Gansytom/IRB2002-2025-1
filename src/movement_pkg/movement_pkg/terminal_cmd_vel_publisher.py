#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import CmdVel
import threading


class TerminalCmdVelPublisher(Node):
    def __init__(self):
        super().__init__("terminal_cmd_vel_publisher")
        
        # Create a publisher for the velocity command
        self.publisher_ = self.create_publisher(CmdVel, "motion/cmd_vel", 10)
        self.get_logger().info("Cmd Vel Node has been started.")

        # Ejecutar input por consola en hilo aparte para no bloquear ROS
        self.input_thread = threading.Thread(target=self.read_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def read_input_loop(self):
        while rclpy.ok():
            line = input("Ingresa alguno de los siguientes comandos:\n- on\n- stop\n- <vel_motor_izquierdo> <vel_motor_derecho>\n")
            parts = line.strip().split()

            msg = CmdVel()
            if str(line) == "on":
                self.get_logger().info("Encendiendo motores...\n")
                msg.command = "on"
                msg.left_velocity = 0.0
                msg.right_velocity = 0.0
            elif str(line) == "stop":
                self.get_logger().info("Deteniendo motores...\n")
                msg.command = "stop"
                msg.left_velocity = 0.0
                msg.right_velocity = 0.0
            else:
                msg.command = "-"
                vel_left = float(parts[0])
                vel_right = float(parts[1])
                
                msg.left_velocity = vel_left
                msg.right_velocity = vel_right

            self.publisher_.publish(msg)
            self.get_logger().info(f"Publicando: {msg.left_velocity}, {msg.right_velocity}\n")
            # Esperar un segundo antes de continuar
            # time.sleep(1)

def main(args=None):
    rclpy.init(args=args)
    node = TerminalCmdVelPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
