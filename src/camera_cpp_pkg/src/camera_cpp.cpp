#include <rclcpp/rclcpp.hpp>
#include <sensor_msgs/msg/image.hpp>
#include <image_transport/image_transport.hpp>
#include <opencv2/opencv.hpp>
#include <cv_bridge/cv_bridge.h>
#include "rclcpp/qos.hpp"

class CompressedPublisher : public rclcpp::Node
{
public:
  CompressedPublisher()
  : Node("camera_cpp")
  {
    // image_transport::ImageTransport it(this->shared_from_this());
    // publisher_ = it.advertise("camera/image_compressed", 10);


    cap_.open(0, cv::CAP_V4L2);  // Abrir cámara con backend V4L2 (Linux)
    if (!cap_.isOpened()) {
      RCLCPP_ERROR(this->get_logger(), "No se pudo abrir la cámara.");
      return;
    }

    // Configurar resolución
    cap_.set(cv::CAP_PROP_FRAME_WIDTH, 640);
    cap_.set(cv::CAP_PROP_FRAME_HEIGHT, 640);

    timer_ = this->create_wall_timer(
      std::chrono::milliseconds(100),
      std::bind(&CompressedPublisher::publish_image, this));
  }
  void init_publisher()
  {
    image_transport::ImageTransport it(shared_from_this());
    rmw_qos_profile_t image_qos = rmw_qos_profile_sensor_data;
    publisher_ = it.advertise("camera/image", image_qos);
  }
private:
  void publish_image()
  {
    cv::Mat frame;
    cap_ >> frame;
    if (frame.empty()) return;
    auto msg = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", frame).toImageMsg();
    publisher_.publish(msg);
  }

  image_transport::Publisher publisher_;
  rclcpp::TimerBase::SharedPtr timer_;
  cv::VideoCapture cap_;
};

int main(int argc, char* argv[])
{
  rclcpp::init(argc, argv);
//   rclcpp::spin(std::make_shared<CompressedPublisher>());
  auto node = std::make_shared<CompressedPublisher>();
  node->init_publisher();
  rclcpp::spin(node);
  rclcpp::shutdown();
  return 0;
}