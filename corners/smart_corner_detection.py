from corners.approach import *
from corners.annealing import *
import time
import cv2
from corners.image_transforms import four_point_transform, plot_grid_on_transformed_image
from corners.corrector import *

def draw_line(img, ln, color, thickness):
    height, width = img.shape[:2]
    sg = get_window_segment(width, height, ln)
    if (sg is None):
        print("bad line", ln)
    else:
        pt1 = (round(sg.pt1.x), round(sg.pt1.y))
        pt2 = (round(sg.pt2.x), round(sg.pt2.y))
        cv2.line(img, pt1, pt2, color, thickness, cv2.LINE_AA)


def draw_circle(img, pt, color, radius):
    x = round(pt.x)
    y = round(pt.y)
    cv2.circle(img, (x, y), radius, color, 1)


def get_corners(src):
    img = src
    img = cv2.resize(img, (416, 416))
    h, w = img.shape[:2]
    src = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    start_time = time.time()
    board = get_approach(src)
    board = simulation(board, src)

    score = calc_score(board, src, True)
    # print(score)
    # print("final_score=", score)
    worst_horizontal = 0
    worst_vertical = 0
    for i in range(BOARD_LINES_CNT):
        if score[1][0][i] < score[1][0][worst_horizontal]:
            worst_horizontal = i
        if score[1][1][i] < score[1][1][worst_vertical]:
            worst_vertical = i
    pts = [board.get_cross(0, 0), board.get_cross(0, BOARD_LINES_CNT - 1), board.get_cross(BOARD_LINES_CNT - 1, BOARD_LINES_CNT - 1), board.get_cross(BOARD_LINES_CNT - 1, 0)]
    n = BOARD_LINES_CNT
    pts[0] = pts[0] + (board.get_cross(0, 0) - board.get_cross(0, 1)) + (board.get_cross(0, 0) - board.get_cross(1, 0))
    pts[2] = pts[2] + 1.1 * (board.get_cross(n-1, n-1) - board.get_cross(n-1, n-2)) + 1.1 * (board.get_cross(n-1, n-1) - board.get_cross(n-2, n-1))
    pts[1] = pts[1] + (board.get_cross(0, n-1) - board.get_cross(1, n-1)) + (board.get_cross(0, n-1) - board.get_cross(0, n-2))
    pts[3] = pts[3] + 1.1 * (board.get_cross(n-1, 0) - board.get_cross(n-1, 1)) + 1.1 * (board.get_cross(n-1, 0) - board.get_cross(n-2, 0))
    # pts = np.array(pts)
    np_pts = np.array([(pts[0].x, pts[0].y), (pts[1].x, pts[1].y), (pts[2].x, pts[2].y), (pts[3].x, pts[3].y)])
    np_pts = random_corrector(img, np_pts)

    # print("!!!", calc_corner_metric(img, np_pts, True))
    # for pt in pts:
    #     draw_circle(img, pt, (0, 255, 0), 5)
    draw_circle(img, Vector(np_pts[0][0], np_pts[0][1]), (0, 255, 0), 3)
    draw_circle(img, Vector(np_pts[1][0], np_pts[1][1]), (0, 255, 0), 3)
    draw_circle(img, Vector(np_pts[2][0], np_pts[2][1]), (0, 255, 0), 3)
    draw_circle(img, Vector(np_pts[3][0], np_pts[3][1]), (0, 255, 0), 3)
    for i in range(BOARD_LINES_CNT):
        # print(i, "vert")
        draw_line(img, board.vertical(i), (255, 0, 0), 1)
        # print(i, "hor")
        draw_line(img, board.horizontal(i), (255, 0, 0), 1)
    draw_line(img, board.horizontal(worst_horizontal), (0, 0, 255), 1)
    draw_line(img, board.vertical(worst_vertical), (0, 0, 255), 1)
    # print("final_time=", time.time() - start_time)
    # big_result = cv2.resize(img, (800, 800))
    # cv2.imshow('big_res ' + str(random.randint(1, 10000)), big_result)
    return np_pts
    # cv2.waitKey()


def detect_corners(img=None, img_filename=None):
    if img is None:
        if img_filename is None:
            return AttributeError("img or img_filename must be not None")
        img = cv2.imread(img_filename)
    corners = get_corners(img)
    transformed_image, M = four_point_transform(img, corners)
    ptsT, ptsL = plot_grid_on_transformed_image(transformed_image, draw=True)
    return corners
