from setuptools import find_packages, setup

package_name = 'movement_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='grupo1',
    maintainer_email='tomas.lopezm20@uc.cl',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'motor_driver_node = movement_pkg.motor_driver_node:main',
            'motor_driver_node_v2 = movement_pkg.motor_driver_node_v2:main',
            'terminal_cmd_vel_publisher = movement_pkg.terminal_cmd_vel_publisher:main',
            'joy_cmd_vel_publisher = movement_pkg.joy_cmd_vel_publisher:main',
            'terminal_cmd_vel_publisher_v2 = movement_pkg.terminal_cmd_vel_publisher_v2:main',
            'motion_planner_node = movement_pkg.motion_planner_node:main',
            'camera_controller_node = movement_pkg.camera_controller_node:main',
            'camera_controller_node_v2 = movement_pkg.camera_controller_node_v2:main',
        ],
    },
)
