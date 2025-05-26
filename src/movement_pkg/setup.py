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
            'motor_controller_node = movement_pkg.motor_controller_node:main',
            'motion_planner_node = movement_pkg.motion_planner_node:main',
            'joy_motor_controller_node = movement_pkg.joy_motor_controller_node:main',
            'joy_velocity_publisher = movement_pkg.joy_velocity_publisher:main',
            'joy_velocity_publisher_diferential = movement_pkg.joy_velocity_publisher_diferential:main',
            'joy_motor_controller_close_loop = movement_pkg.joy_motor_controller_close_loop:main',
        ],
    },
)
