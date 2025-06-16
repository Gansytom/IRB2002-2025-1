import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from my_robot_interfaces.msg import CmdVel
from sensor_msgs.msg import Joy

class JoyVelocityPublisher(Node):

    def __init__(self):
        # initializa
        super().__init__('joy_velocity_publisher')
        qos_profile = QoSProfile(depth=10)

        # define parámetros
        self._linear_scale = 100
        self._turn_on = False

        # inicia suscriptores
        self.joy_status = self.create_subscription(Joy, '/joy', self.joy_callback, QoSReliabilityPolicy.RELIABLE)

        # inicia publicadores
        self.robot_vel = self.create_publisher(CmdVel, '/motion/cmd_vel', qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info(f"{self.nodeName} started")

        now = self.get_clock().now()


    def joy_callback(self, msg):
        # IMPORTANTE: La asignación de botones se debe verificar
        # para cada controlador en particular...
        # A_button = msg.buttons[0]
        # B_button = msg.buttons[1]
        # X_button = msg.buttons[2]
        # Y_button = msg.buttons[3]
        # LB_button = msg.buttons[4]
        RB_button = msg.buttons[5]
        # LT_button = msg.buttons[8] # No asignado
        # RT_button = msg.buttons[9] # No asignado
        SELECT_button = msg.buttons[6]
        START_button = msg.buttons[7]
        # LSTICK_button = msg.buttons[9]
        # RSTICK_button = msg.buttons[10]
        LSTICK_x_axis = msg.axes[0]
        LSTICK_y_axis = msg.axes[1]
        RSTICK_x_axis = msg.axes[3]
        RSTICK_y_axis = msg.axes[4]
        # LT_axis = msg.axes[2]
        # RT_axis = msg.axes[5]
        #DIR_X = msg.axes[6] # No se cual es
        #DIR_Y = msg.axes[7] # No se cual es
        
        if START_button and not self._turn_on:
            self._turn_on = True
            self.get_logger().info("Turning on motors ...\n")
            # prepara y publica un mensaje para detener el robot
            cmd_vel = CmdVel()
            cmd_vel.command = "on"
            cmd_vel.left_velocity = 0.0
            cmd_vel.right_velocity = 0.0
            self.robot_vel.publish(cmd_vel)
            return
        
        if SELECT_button and self._turn_on:
            self._turn_on = False
            self.get_logger().info("Stopping motors ...\n")
            # prepara y publica un mensaje para detener el robot
            cmd_vel = CmdVel()
            cmd_vel.command= "stop"
            cmd_vel.left_velocity = 0.0
            cmd_vel.right_velocity = 0.0
            self.robot_vel.publish(cmd_vel)
            return
            
        if RB_button and self._turn_on:
            # prepara y publica un mensaje para la velocidad
            cmd_vel = CmdVel()
            cmd_vel.command = "-"
            cmd_vel.left_velocity = LSTICK_y_axis * self._linear_scale
            cmd_vel.right_velocity = RSTICK_y_axis * self._linear_scale
            self.get_logger().info(f"Publishing: {cmd_vel.left_velocity}, {cmd_vel.right_velocity}\n")
            self.robot_vel.publish(cmd_vel)

def main(args=None):
    try:
        rclpy.init(args=args)
        joy_velocity_publisher = JoyVelocityPublisher()
        rclpy.spin(joy_velocity_publisher)
    except KeyboardInterrupt: 
        pass
    except Exception as e:
        print(e)

if __name__ == '__main__':
    main()