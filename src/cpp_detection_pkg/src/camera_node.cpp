#include "rclcpp/rclcpp.hpp"
#include "sensor_msgs/msg/image.hpp"
#include "cv_bridge/cv_bridge.h"
#include "opencv2/opencv.hpp"

using std::placeholders::_1;
using namespace std::chrono_literals;

class CameraNode : public rclcpp::Node
{
public:
    CameraNode() : Node("camera_node")
    {
        RCLCPP_INFO(this->get_logger(), "Initializing camera...");

        cap_.open(0, cv::CAP_V4L);
        cap_.set(cv::CAP_PROP_FRAME_WIDTH, 640);
        cap_.set(cv::CAP_PROP_FRAME_HEIGHT, 640);

        if (!cap_.isOpened())
        {
            throw std::runtime_error("Could not open video device");
        }

        cv::Mat img;
        bool ret = cap_.read(img);
        if (!ret || img.empty())
        {
            throw std::runtime_error("Could not read image from video device");
        }

        RCLCPP_INFO(this->get_logger(), "Camera initialized successfully");

        img_publisher_ = this->create_publisher<sensor_msgs::msg::Image>(
            "camera_topic",
            rclcpp::SensorDataQoS());

        timer_ = this->create_wall_timer(
            100ms,
            std::bind(&CameraNode::timer_callback, this));

        RCLCPP_INFO(this->get_logger(), "Camera node started");
    }

private:
    void timer_callback()
    {
        cv::Mat frame;
        bool ret = cap_.read(frame);
        if (!ret || frame.empty())
        {
            RCLCPP_ERROR(this->get_logger(), "Failed to read image from camera");
            return;
        }

        try
        {
            auto msg = cv_bridge::CvImage(std_msgs::msg::Header(), "bgr8", frame).toImageMsg();
            msg->header.stamp = this->now();
            img_publisher_->publish(*msg);
            RCLCPP_INFO(this->get_logger(), "Publishing image");
        }
        catch (const cv_bridge::Exception &e)
        {
            RCLCPP_ERROR(this->get_logger(), "Error converting image: %s", e.what());
        }
    }

    cv::VideoCapture cap_;
    rclcpp::Publisher<sensor_msgs::msg::Image>::SharedPtr img_publisher_;
    rclcpp::TimerBase::SharedPtr timer_;
};

int main(int argc, char *argv[])
{
    rclcpp::init(argc, argv);
    auto node = std::make_shared<CameraNode>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}