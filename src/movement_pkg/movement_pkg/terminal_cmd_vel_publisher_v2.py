#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from my_robot_interfaces.msg import CmdVel
import threading
import time


class TerminalCmdVelPublisher(Node):
    def __init__(self):
        super().__init__("terminal_cmd_vel_publisher_v2")
        
        # ----- Timers, publishers, suscribers and services -----
        self.publisher_ = self.create_publisher(CmdVel, "motion/cmd_vel", 10)
        self.get_logger().info("Cmd Vel Node has been started.")

        # ----- Reading input from console in a separate thread to avoid blocking ROS -----
        self.input_thread = threading.Thread(target=self.read_input_loop)
        self.input_thread.daemon = True
        self.input_thread.start()

    def limit_velocity(self, velocity): # Limit the velocity to a range of -100 to 100
        return max(min(velocity, 100.0), -100.0)

    def read_input_loop(self): # Read input from the console in a loop
        while rclpy.ok():
            cmd = input("Ingresa alguno de los siguientes comandos:\n- on\n- stop\n- move\n- shovel\n")

            msg = CmdVel()
            if str(cmd) == "on":
                self.get_logger().info("Encendiendo motores...\n")
                msg.command = "on"
                msg.left_velocity = 0.0
                msg.right_velocity = 0.0
                self.publisher_.publish(msg)
            elif str(cmd) == "stop":
                self.get_logger().info("Deteniendo motores...\n")
                msg.command = "stop"
                msg.left_velocity = 0.0
                msg.right_velocity = 0.0
                self.publisher_.publish(msg)
            elif str(cmd) == "move":
                vel_cmd = input("Ingresa velocidades: <vel_motor_izquierdo> <vel_motor_derecho>\n")
                vel_cmd = vel_cmd.strip().split()
                
                if len(vel_cmd) != 2 or \
                    not all(v.replace('.', '', 1).lstrip('-').isdigit() for v in vel_cmd):
                    self.get_logger().error("\nFormato de velocidades incorrecto. Debe ser: <vel_motor_izquierdo> <vel_motor_derecho>\n")
                    continue

                self.get_logger().info("Moviendo motores...\n")
                msg.command = "move"
                vel_left = float(vel_cmd[0])
                vel_right = float(vel_cmd[1])
                vel_left = self.limit_velocity(vel_left)
                vel_right = self.limit_velocity(vel_right)
                msg.left_velocity = vel_left
                msg.right_velocity = vel_right

                self.publisher_.publish(msg)
            
            elif str(cmd) == "shovel":
                vel_cmd = input("Ingresa velocidad: <vel_pala>\n")

                if len(vel_cmd.strip().split()) != 1 or \
                   not vel_cmd.strip().replace('.', '', 1).lstrip('-').isdigit():
                    self.get_logger().error("\nFormato de velocidades incorrecto. Debe ser: <vel_pala>\n")
                    continue

                self.get_logger().info("Moviendo pala...\n")
                msg.command = "shovel"
                vel_shovel = float(vel_cmd.strip())
                vel_shovel = self.limit_velocity(vel_shovel)
                msg.left_velocity = vel_shovel
                msg.right_velocity = vel_shovel

                self.publisher_.publish(msg)

            else:
                self.get_logger().error("\nComando no reconocido. Intente de nuevo.\n")
                continue
            
            time.sleep(0.1)

def main(args=None):
    rclpy.init(args=args)
    node = TerminalCmdVelPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
