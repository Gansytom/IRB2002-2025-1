#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import cv2
import time
from cv_bridge import CvBridge
import numpy as np
from ultralytics import YOLO
from sensor_msgs.msg import CompressedImage
from my_robot_interfaces.msg import Bottle, BottleArray


class PredictionNode(Node):
    def __init__(self):
        super().__init__("prediction_node")
        self.bridge = CvBridge()

        # ----- Timers, publishers, suscribers and services -----
        self.publisher_ = self.create_publisher(BottleArray, "/bottle_detections", qos_profile=qos_profile_sensor_data)
        self.img_suscriber_ = self.create_subscription(
            CompressedImage,
            "/camera/image/compressed",            
            self.img_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.get_logger().info("Prediction node started")
        # ----- Parameters -----
        self.frame = None
        self.annotated_frame = None
        self.results = None

        model_path = "/home/tomy/IRB2002-2025-1/src/detection_pkg/detection_pkg/modelo.pt"
        #model_path = "IRB2002-2025-1/src/detection_pkg/detection_pkg/best_yolo11_ncnn_model"
        self.model = YOLO(model_path)
        self.labels = ["Botellas"]
        self.get_logger().info("Model loaded successfully")

        self.bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
              (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

        self.avg_frame_rate = 0
        self.frame_rate_buffer = []
        self.fps_avg_len = 200
        self.img_count = 0

        self.above_distance_factor = 0.6
        self.below_distance_factor = 1.4
        self.align_threshold = 100

    def img_callback(self, msg):
        t_start = time.perf_counter()
        # Convert the ROS Image message to OpenCV format
        np_arr = np.frombuffer(msg.data, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        img_width = frame.shape[1]
        img_height = frame.shape[0]
        # frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")

        # Run inference on frame
        results = self.model(frame, verbose=False)
        detections = results[0].boxes

        object_count = 0
        pub_msg = BottleArray()

        # Go through each detection and get bbox coords, confidence, and class
        id = 0
        for i in range(len(detections)):
            bottle = Bottle()
            
            xyxy_tensor = detections[i].xyxy.cpu() # Detections in Tensor format in CPU memory
            xyxy = xyxy_tensor.numpy().squeeze() # Convert tensors to Numpy array
            xmin, ymin, xmax, ymax = xyxy.astype(int) # Extract individual coordinates and convert to int

            width = int(abs(xmax - xmin))
            height = int(abs(ymax - ymin))
            x = abs(xmin - xmax)/2
            y = abs(ymin - ymax)/2

            # Get bounding box class ID and name
            classidx = int(detections[i].cls.item())
            classname = self.labels[classidx]

            # Get bounding box confidence
            conf = detections[i].conf.item()

            
            bottle.id = id
            id += 1
            bottle.probability = conf
            bottle.x = xmin + x
            bottle.y = ymin + y
            bottle.width = width
            bottle.height = height
            bottle.img_width = img_width
            bottle.img_height = img_height
            pub_msg.bottles.append(bottle)
            # Draw box if confidence threshold is high enough
            if conf > 0.45:

                color = self.bbox_colors[classidx % 10]
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)

                label = f'{classname}: {int(conf*100)}%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED) # Draw white box to put label text in
                cv2.circle(frame, (int(xmin + x), int(ymin + y)), 5, (0, 255, 0), -1)
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) # Draw label text

                # Basic example: count the number of objects in the image
                object_count = object_count + 1

        # Draw criteria axis
        cv2.line(frame, (0, int(img_height/2 * self.below_distance_factor)), (img_width, int(img_height/2 * self.below_distance_factor)), (255, 0, 0), 1)
        cv2.line(frame, (0, int(img_height/2 * self.above_distance_factor)), (img_width, int(img_height/2 * self.above_distance_factor)), (255, 0, 0), 1)
        cv2.line(frame, (int(img_width/2 - self.align_threshold), 0), (int(img_width/2 - self.align_threshold), img_height), (255, 0, 0), 1)
        cv2.line(frame, (int(img_width/2 + self.align_threshold), 0), (int(img_width/2 + self.align_threshold), img_height), (255, 0, 0), 1)

        # Calculate and draw framerate (if using video, USB, or Picamera source)
        cv2.putText(frame, f'FPS: {self.avg_frame_rate:0.2f}', (10,20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) # Draw framerate
        
        # Display detection results
        cv2.putText(frame, f'Number of objects: {object_count}', (10,40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) # Draw total number of detected objects
        cv2.imshow('YOLO detection results',frame) # Display image

        cv2.waitKey(1)

        # Calculate FPS for this frame
        t_stop = time.perf_counter()
        frame_rate_calc = float(1/(t_stop - t_start))

        # Append FPS result to frame_rate_buffer (for finding average FPS over multiple frames)
        if len(self.frame_rate_buffer) >= self.fps_avg_len:
            temp = self.frame_rate_buffer.pop(0)
            self.frame_rate_buffer.append(frame_rate_calc)
        else:
            self.frame_rate_buffer.append(frame_rate_calc)

        # Calculate average FPS for past frames
        self.avg_frame_rate = np.mean(self.frame_rate_buffer)
        pub_msg.number = id
        self.publisher_.publish(pub_msg)
        

def main(args=None):
    rclpy.init(args=args)
    node = PredictionNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
