from ultralytics import YOLO
import cv2
import yadisk

def download_model(path):
    print("Started downloading model")
    # url to get token: REMOVED
    yandex_disk_token = "REMOVED"
    disk_path = "Модель шахмат/warmup_normal_final.pt"
    disk = yadisk.YaDisk(token=yandex_disk_token)
    disk.download(disk_path, path)
    print("Download finished")

def load_model(path):
    try:
        return YOLO(path)
    except:
        print("Failed to load model")
        download_model(path)
        return YOLO(path)

def chess_pieces_detector(image, model):
    results = model.predict(source=image, conf=0.5, augment=False, save=False)
    res_plotted = results[0].plot(line_width=1, font_size=1)
    cv2.imwrite("temp/detection.jpg", res_plotted)
    boxes = results[0].boxes.cpu()
    detections = boxes.xyxy.numpy()
    return detections, boxes
