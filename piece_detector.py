from ultralytics import YOLO
import cv2


def load_model(path):
    return YOLO(path)


def chess_pieces_detector(image, model):
    results = model.predict(source=image, line_width=1, conf=0.3, augment=False, save=False)
    res_plotted = results[0].plot()
    cv2.imwrite("temp/detection.jpg", res_plotted)
    boxes = results[0].boxes.cpu()
    detections = boxes.xyxy.numpy()
    return detections, boxes
