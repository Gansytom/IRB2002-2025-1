#!/usr/bin/env python3
import rclpy
from rclpy.qos import qos_profile_sensor_data
from rclpy.node import Node
import cv2
import os
import sys
import time
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
from ultralytics import YOLO
import numpy as np


class PredictionNode(Node):
    def __init__(self):
        super().__init__("prediction_node")
        self.bridge = CvBridge()

        # Create a suscriber for images
        self.img_suscriber_ = self.create_subscription(
            Image,
            "camera_topic",
            self.img_callback,
            qos_profile=qos_profile_sensor_data
        )
        self.get_logger().info("Prediction node started")

        #model_path = 'IRB2002-2025-1/src/detection_pkg/detection_pkg/best.pt'
        self.user_res = None
        self.record = False
        self.resize = False
        self.resW = 640
        self.resH = 640
        
        model_path = "IRB2002-2025-1/src/detection_pkg/detection_pkg/best.pt"
        # Check if model file exists and is valid
        if (not os.path.exists(model_path)):
            print('ERROR: Model path is invalid or model was not found. Make sure the model filename was entered correctly.')
            sys.exit(0)
        #self.model = YOLO(model_path)
        # Load the model into memory and get labemap
        self.model = YOLO(model_path, task='detect')
        self.labels = ["Botellas"]
        self.get_logger().info("Model loaded successfully")
        
        # Set bounding box colors (using the Tableu 10 color scheme)
        self.bbox_colors = [(164,120,87), (68,148,228), (93,97,209), (178,182,133), (88,159,106), 
                    (96,202,231), (159,124,168), (169,162,241), (98,118,150), (172,176,184)]

        # Initialize control and status variables
        self.avg_frame_rate = 0
        self.frame_rate_buffer = []
        self.fps_avg_len = 200
        self.img_count = 0

    def img_callback(self, msg):
        self.get_logger().info("Image received")
        # Convert the ROS Image message to OpenCV format
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        results = self.model.predict(frame, imgsz=640, conf=0.5)
        annotated_frame = results[0].plot()

        t_start = time.perf_counter()
        # Resize frame to desired display resolution
        if self.resize == True:
            frame = cv2.resize(frame,(self.resW,self.resH))

        # Run inference on frame
        results = self.model(frame, verbose=False)

        # Extract results
        detections = results[0].boxes

        # Initialize variable for basic object counting example
        object_count = 0

        # Go through each detection and get bbox coords, confidence, and class
        for i in range(len(detections)):
            self.get_logger().info("Object detected")

            # Get bounding box coordinates
            # Ultralytics returns results in Tensor format, which have to be converted to a regular Python array
            xyxy_tensor = detections[i].xyxy.cpu() # Detections in Tensor format in CPU memory
            xyxy = xyxy_tensor.numpy().squeeze() # Convert tensors to Numpy array
            xmin, ymin, xmax, ymax = xyxy.astype(int) # Extract individual coordinates and convert to int

            # Get bounding box class ID and name
            classidx = int(detections[i].cls.item())
            classname = self.labels[classidx]

            # Get bounding box confidence
            conf = detections[i].conf.item()

            # Draw box if confidence threshold is high enough
            if conf > 0.5:

                color = self.bbox_colors[classidx % 10]
                cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), color, 2)

                label = f'{classname}: {int(conf*100)}%'
                labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1) # Get font size
                label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), color, cv2.FILLED) # Draw white box to put label text in
                cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1) # Draw label text

                # Basic example: count the number of objects in the image
                object_count = object_count + 1

        # Calculate and draw framerate (if using video, USB, or Picamera source)
        cv2.putText(frame, f'FPS: {self.avg_frame_rate:0.2f}', (10,20), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) # Draw framerate
        
        # Display detection results
        cv2.putText(frame, f'Number of objects: {object_count}', (10,40), cv2.FONT_HERSHEY_SIMPLEX, .7, (0,255,255), 2) # Draw total number of detected objects
        cv2.imshow('YOLO detection results',frame) # Display image

        # Calculate FPS for this frame
        t_stop = time.perf_counter()
        frame_rate_calc = float(1/(t_stop - t_start))

        # Append FPS result to frame_rate_buffer (for finding average FPS over multiple frames)
        if len(self.frame_rate_buffer) >= self.fps_avg_len:
            self.frame_rate_buffer.append(frame_rate_calc)
        else:
            self.frame_rate_buffer.append(frame_rate_calc)

        # Calculate average FPS for past frames
        self.avg_frame_rate = np.mean(self.frame_rate_buffer)
    

def main(args=None):
    rclpy.init(args=args)
    node = PredictionNode()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
