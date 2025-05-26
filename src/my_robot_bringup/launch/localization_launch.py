import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():

    # Set the path to different files and folders.
    pkg_share = FindPackageShare(package='basic_mobile_robot').find('basic_mobile_robot')
    robot_localization_file_path = os.path.join(pkg_share, 'config/ekf.yaml') 

    # Specify the actions

    # Start robot localization using an Extended Kalman filter
    start_robot_localization_cmd = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[robot_localization_file_path])

    # Node: turtlesim_node
    turtlesim_node = Node(
        package='turtlesim',
        executable='turtlesim_node',
        name='turtlesim')

    # Node: turtle_teleop_key
    turtle_teleop_key_node = Node(
        package='turtlesim',
        executable='turtle_teleop_key',
        name='teleop',
        output='screen')

    # Create the launch description and populate
    ld = LaunchDescription()

    # Add any actions
    ld.add_action(start_robot_localization_cmd)
    ld.add_action(turtlesim_node)
    ld.add_action(turtle_teleop_key_node)

    return ld
