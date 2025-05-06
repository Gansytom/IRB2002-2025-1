cmake_minimum_required(VERSION 3.8)
project(cpp_detection_pkg)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(examples_interfaces REQUIRED)

add_executable(camera_node src/camera_node.cpp)

install(TARGETS 
  camera_node
  DESTINATION lib/${PROJECT_NAME}
  )

ament_package()
