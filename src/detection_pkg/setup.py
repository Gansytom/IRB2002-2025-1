from setuptools import find_packages, setup

package_name = 'detection_pkg'

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
    maintainer_email='grupo1@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'camera_node = detection_pkg.camera_node:main',
            'test = detection_pkg.test:main',
            'prediction_node = detection_pkg.prediction_node:main',
            'yolov8_node = detection_pkg.yolov8_node:main',
            'yolov11_node = detection_pkg.yolov11_node:main',
        ],
    },
)
