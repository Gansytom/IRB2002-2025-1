#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from ultralytics import YOLO
import cv2
import os


class CameraNode(Node):
    def __init__(self):
        super().__init__("camera_node")

        # Initialize the camera
        self.get_logger().info("Initializing camera...")
        self.vid = cv2.VideoCapture(0)
        if not self.vid.isOpened():
            raise ValueError("Could not open video device")
        ret, img = self.vid.read()
        if not ret or img is None:
            raise ValueError("Could not read image from video device")
        self.get_logger().info("Camera initialized successfully")
        # Cargar el modelo
        cwd = os.getcwd()
        model_path = 'IRB2002-2025-1/src/detection_pkg/detection_pkg/best.pt'
        self.model = YOLO(model_path)

def main(args=None):
    rclpy.init(args=args)
    node = CameraNode()
    while(True):
        ret, frame = node.vid.read()
        small_frame = cv2.resize(frame, (640, 640))

        results = node.model.predict(frame, imgsz=640, conf=0.5)
        annotated_frame = results[0].plot()
        
        #cv2.imshow('frame',frame)
        cv2.imshow("YOLOv8 Detection", annotated_frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

    node.vid.release() # Cuando se termina el programa, se libera la camara por parte del software
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()