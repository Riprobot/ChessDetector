import cv2
from corners.smart_corner_detection import detect_corners
from corners.image_transforms import four_point_transform, plot_grid_on_transformed_image, \
    get_perspective_point, \
    get_point_by_box
from pieces.piece_detector import chess_pieces_detector
from pieces.piece_detector import load_model
import numpy as np
import time


class FEN_Converter:
    def __init__(self, model_path):
        self.model = load_model(model_path)
        self.num2chess = {
            0: 'b', 1: 'k', 2: 'n',
            3: 'p', 4: 'q', 5: 'r',
            6: 'B', 7: 'K', 8: 'N',
            9: 'P', 10: 'Q', 11: 'R'}

    def reverseFENBoard(self, FENBoard):
        FEN_annotation = [['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1']]
        for i in range(len(FENBoard)):
            for j in range(len(FENBoard)):
                FEN_annotation[i][j] = FENBoard[j][7 - i]
        return FEN_annotation

    def convert_fen(self, image_path):
        board_size = 8
        print("Started to detect")
        img = cv2.imread(image_path)
        # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.resize(img, (416, 416))
        now = time.time()
        corners = detect_corners(img=img)
        print(f"Corners detected in {time.time() - now} s.")
        transformed_image, M = four_point_transform(img, corners)
        detections, boxes = chess_pieces_detector(img, self.model)
        width = transformed_image.size[0]
        height = transformed_image.size[1]
        dy = width / board_size
        dx = height / board_size
        FEN_annotation = [['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1'],
                          ['1', '1', '1', '1', '1', '1', '1', '1']]
        sorted_by_conf = [i for i in range(len(detections))]
        print(boxes)
        sorted_by_conf = sorted(sorted_by_conf, key=lambda x: boxes.conf[x].item())
        for _ in range(len(detections)):
            id = sorted_by_conf[_]
            box = detections[id]
            pts = get_perspective_point(get_point_by_box(box), M)
            if pts[0] >= 0 and pts[0] < width and pts[1] >= 0 and pts[1] < height:
                y = int(pts[0] / dy)
                x = int(pts[1] / dx)
                FEN_annotation[x][y] = self.num2chess[boxes.cls[id].item()]
            else:
                print(f"Not found {self.num2chess[boxes.cls[id].item()]}")
        FEN_annotation = self.reverseFENBoard(FEN_annotation)
        complete_board_FEN = [''.join(line) for line in FEN_annotation]
        return complete_board_FEN

    def get_lichess_editor(self, image_path):
        complete_board_FEN = self.convert_fen(image_path)
        to_FEN = '/'.join(complete_board_FEN)
        return "https://lichess.org/editor/" + to_FEN

    def get_lichess_analysis(self, image_path):
        complete_board_FEN = self.convert_fen(image_path)
        to_FEN = '/'.join(complete_board_FEN)
        return "https://lichess.org/analysis/" + to_FEN
