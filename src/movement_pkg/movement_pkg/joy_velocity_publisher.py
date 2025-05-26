import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy

class JoyVelocityPublisher(Node):

    def __init__(self):
        # initializa
        super().__init__('joy_velocity_publisher')
        qos_profile = QoSProfile(depth=10)

        # define parámetros
        self._linear_scale = 255
        self._angular_scale = 255

        # inicia suscriptores
        self.joy_status = self.create_subscription(Joy, '/joy', self.joy_callback, QoSReliabilityPolicy.RELIABLE)

        # inicia publicadores
        self.robot_vel = self.create_publisher(Twist, '/motion/cmd_vel', qos_profile)
        self.nodeName = self.get_name()
        self.get_logger().info(f"{self.nodeName} started")

        now = self.get_clock().now()


    def joy_callback(self, msg):
        # IMPORTANTE: La asignación de botones se debe verificar
        # para cada controlador en particular...
        A_button = msg.buttons[0]
        B_button = msg.buttons[1]
        X_button = msg.buttons[2]
        Y_button = msg.buttons[3]
        LB_button = msg.buttons[4]
        RB_button = msg.buttons[5]
        # LT_button = msg.buttons[8] # No asignado
        # RT_button = msg.buttons[9] # No asignado
        SELECT_button = msg.buttons[6]
        START_button = msg.buttons[7]
        LSTICK_button = msg.buttons[9]
        RSTICK_button = msg.buttons[10]
        LSTICK_x_axis = msg.axes[0]
        LSTICK_y_axis = msg.axes[1]
        RSTICK_x_axis = msg.axes[3]
        RSTICK_y_axis = msg.axes[4]
        LT_axis = msg.axes[2]
        RT_axis = msg.axes[5]
        #DIR_X = msg.axes[6] # No se cual es
        #DIR_Y = msg.axes[7] # No se cual es
        # if A_button:
        #     self.get_logger().info(f"Button A pressed")
        # if B_button:
        #     self.get_logger().info(f"Button B pressed")
        # if X_button:
        #     self.get_logger().info(f"Button X pressed")
        # if Y_button:
        #     self.get_logger().info(f"Button Y pressed")
        # if LB_button:
        #     self.get_logger().info(f"Left bumper pressed")
        # if RB_button:
        #     self.get_logger().info(f"Right bumper pressed")
        # if SELECT_button:
        #     self.get_logger().info(f"Select button pressed")
        # if START_button:
        #     self.get_logger().info(f"Start button pressed")
        # if LSTICK_button:
        #     self.get_logger().info(f"Left stick button pressed")
        # if RSTICK_button:
        #     self.get_logger().info(f"Right stick button pressed")
        
        # self.get_logger().info(f"Left stick x: {LSTICK_x_axis}, y: {LSTICK_y_axis}")
        #self.get_logger().info(f"Right stick x: {RSTICK_x_axis}, y: {RSTICK_y_axis}")
        #self.get_logger().info(f"Left trigger axis: {LT_axis}, Right trigger axis: {RT_axis}")
        # self.get_logger().info(f"Direction x: {DIR_X}, y: {DIR_Y}")

        if RB_button:
            self.get_logger().info(f"Left axes x: {LSTICK_x_axis}, y: {LSTICK_y_axis}")
            # prepara y publica un mensaje para la velocidad
            cmd_vel = Twist()
            cmd_vel.linear.x = LSTICK_y_axis * self._linear_scale
            cmd_vel.angular.z = LSTICK_x_axis * self._angular_scale
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