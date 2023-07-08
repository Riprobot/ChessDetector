from corners.approach import *
from corners.annealing import *
import time
import cv2
from corners.image_transforms import four_point_transform, plot_grid_on_transformed_image
from corners.corrector import *
from os import listdir
from os.path import isfile, join
import platform
import subprocess
executable_path = {
    "Windows": "Windows/board_finder_calc.exe",
    "Linux": "Linux/board_finder_calc",
    "Darwin": "Darwin/board_finder_calc"
}

# def draw_line(img, ln, color, thickness):
#     height, width = img.shape[:2]
#     sg = get_window_segment(width, height, ln)
#     if (sg is None):
#         print("bad line", ln)
#     else:
#         pt1 = (round(sg.pt1.x), round(sg.pt1.y))
#         pt2 = (round(sg.pt2.x), round(sg.pt2.y))
#         cv2.line(img, pt1, pt2, color, thickness, cv2.LINE_AA)


# def draw_circle(img, pt, color, radius):
#     x = round(pt.x)
#     y = round(pt.y)
#     cv2.circle(img, (x, y), radius, color, 1)

def run_annealing_executable(board):
    h, w = board.img.shape[:2]
    src = board.img
    file_start_time = time.time()
    f = open("temp/board_find_data.txt", 'w')
    f.write(str(h) + " " + str(w) + "\n")
    for i in range(h):
        for j in range(w):
            s = hex(src[i, j])[2:]
            if (len(s) == 1):
                s = '0' + s
            f.write(s + " ")
    f.write("\n")
    for i in range(BOARD_LINES_CNT):
        f.write(str(board.left[i]) + " ")
    for i in range(BOARD_LINES_CNT):
        f.write(str(board.right[i]) + " ")
    for i in range(BOARD_LINES_CNT):
        f.write(str(board.up[i]) + " ")
    for i in range(BOARD_LINES_CNT):
        f.write(str(board.down[i]) + " ")

    f.close()
    file_end_time = time.time()
    print("file time =", file_end_time - file_start_time)
    try:
        outside_start_time = time.time()
        subprocess.run([f"./corners/annealing_executables/{executable_path[platform.system()]}"])
        board_coordinates = []
        with open('temp/corners.txt') as f:
            lines = f.readlines()
            for line in lines:
                board_coordinates.append(list(map(int, line.split())))
        board = Board(board_coordinates[0], board_coordinates[1], board_coordinates[2], board_coordinates[3], src)
        outside_end_time = time.time()
        print("outside time =", outside_end_time - outside_start_time)
        return board
    except:
        print("executable run failure, running python")
        return None

def get_corners(src, use_executables):
    img = src
    img = cv2.resize(img, (416, 416))
    h, w = img.shape[:2]
    src = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    start_time = time.time()
    board = get_approach(src)
    if use_executables:
        new_board = run_annealing_executable(board)
        if new_board is not None:
            board = new_board
        else:
            board = simulation(board)
    else:
        board = simulation(board)
    score = calc_score(board, True)
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
    # draw_circle(img, Vector(np_pts[0][0], np_pts[0][1]), (0, 255, 0), 3)
    # draw_circle(img, Vector(np_pts[1][0], np_pts[1][1]), (0, 255, 0), 3)
    # draw_circle(img, Vector(np_pts[2][0], np_pts[2][1]), (0, 255, 0), 3)
    # draw_circle(img, Vector(np_pts[3][0], np_pts[3][1]), (0, 255, 0), 3)
    # for i in range(BOARD_LINES_CNT):
    #     draw_line(img, board.vertical(i), (255, 0, 0), 1)
    #     draw_line(img, board.horizontal(i), (255, 0, 0), 1)
    # draw_line(img, board.horizontal(worst_horizontal), (0, 0, 255), 1)
    # draw_line(img, board.vertical(worst_vertical), (0, 0, 255), 1)
    # print("final_time=", time.time() - start_time)
    # big_result = cv2.resize(img, (800, 800))
    # cv2.imshow('big_res ' + str(random.randint(1, 10000)), big_result)
    return np_pts
    # cv2.waitKey()


def detect_corners(img=None, img_filename=None, use_executables=True):
    if img is None:
        if img_filename is None:
            raise AttributeError("img or img_filename must be not None")
        img = cv2.imread(img_filename)
    corners = get_corners(img, use_executables)
    transformed_image, M = four_point_transform(img, corners)
    ptsT, ptsL = plot_grid_on_transformed_image(transformed_image, draw=True)
    return corners
