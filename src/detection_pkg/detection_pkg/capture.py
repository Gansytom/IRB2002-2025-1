from ultralytics import YOLO
import numpy as np
import cv2


nCam = 0 # Valor de la camara, 0 es la del notebook
cap = cv2.VideoCapture(nCam, cv2.CAP_DSHOW) 

# cap = cv2.VideoCapture(nCam)

# Cargar el modelo
model_path = 'best.pt'
model = YOLO(model_path)


while(True):
    ret, frame = cap.read()
    small_frame = cv2.resize(frame, (640, 480))

    results = model.predict(frame, imgsz=640, conf=0.5)
    annotated_frame = results[0].plot()
    
    cv2.imshow('frame',frame)
    cv2.imshow("YOLOv8 Detection", annotated_frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release() # Cuando se termina el programa, se libera la camara por parte del software
cv2.destroyAllWindows()