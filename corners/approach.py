from corners.annealing import *
import numpy as np
import cv2

def is_same_lines(w, h, ln1, ln2):
    dot = ln1.cross(ln2)
    if dot is not None and inside_window(w, h, dot):
        return True
    return smooth_distance(w, h, ln1, ln2) < 10


def get_cross_diff(img, ln1, ln2):
    h, w = img.shape[:2]
    dot = ln1.cross(ln2)
    d1 = ln1.direction().normalize()
    d2 = ln2.direction().normalize()
    RADIUS = 5
    sm = [0, 0, 0, 0]
    cnt = [0, 0, 0, 0]
    # a = []
    # for i in range(-RADIUS, RADIUS):
    #     b = []
    #     for j in range(-RADIUS, RADIUS):
    #         b.append('#')
    #     a.append(b)

    for i in range(-RADIUS, RADIUS + 1):
        if i == 0:
            continue
        for j in range(-RADIUS, RADIUS + 1):
            if j == 0:
                continue
            x = round(dot.x + i * d1.x + j * d2.x)
            y = round(dot.y + i * d1.y + j * d2.y)
            index = 0
            if i > 0 and j > 0:
                index = 0
            elif i > 0 and j < 0:
                index = 1
            elif i < 0 and j < 0:
                index = 2
            elif i < 0 and j > 0:
                index = 3
            if (0 <= x < w and 0 <= y < h):
                # print("!", x, y, w, h)
                pixel_color = img[y, x]
                # a[i + RADIUS][j + RADIUS] = pixel_color
                weight = (1 / min(abs(i), abs(j)))
                sm[index] += pixel_color * weight
                cnt[index] += weight
    for i in range(4):
        if (cnt[i] == 0):
            # print("wtf")
            return -255 * 4
    color = [(sm[0] / cnt[0]), (sm[1] / cnt[1]), (sm[2] / cnt[2]), (sm[3] / cnt[3])]
    # for i in a:
    #     print('\t'.join(map(str, i)))
    # print("color=", color)
    result = 0
    for i in range(4):
        result += abs(color[i] - color[(i + 1) % 4])
    result -= 2 * abs(color[0] - color[2])
    result -= 2 * abs(color[1] - color[3])
    # if (result >= 190):
    #     cool_dots.append(dot)
    return result

def find_inner_lines(img, lines, inside_lines_cnt=7, angle_fl=False, h_angle=0, v_angle=0):
    height, width = img.shape[:2]
    vertical_lines = []
    horizontal_lines = []
    h_angle_delta = 7
    v_angle_delta = 20
    vertical_angles = []
    horizontal_angles = []
    for cur_line in lines:
        dx = cur_line.direction().x
        dy = cur_line.direction().y
        angle = math.atan2(-dy, dx)
        if angle < 0:
            angle += math.pi
        angle = angle / math.pi * 180
        angle = min(angle, 180 - angle)
        if ((not angle_fl and 0 <= angle <= h_angle_delta) or (angle_fl and (abs(angle - h_angle) <= 2))):
            fl = True
            for line in horizontal_lines:
                # if smooth_distance(width, height, line, cur_line) < 20:
                if is_same_lines(width, height, line, cur_line):
                    fl = False
                    break
            if fl:
                horizontal_lines.append(cur_line)
                horizontal_angles.append(angle)
        if ((not angle_fl and 90 - v_angle_delta <= angle <= 90 + v_angle_delta) or (
                angle_fl and abs(angle - v_angle) <= 15)):
            fl = True
            for line in vertical_lines:
                # if smooth_distance(width, height, line, cur_line) < 20:
                if is_same_lines(width, height, line, cur_line):
                    fl = False
                    break
            if fl:
                vertical_lines.append(cur_line)
                vertical_angles.append(angle)
    horizontal_good = [True] * len(horizontal_lines)
    horizontal_cnt = len(horizontal_lines)
    vertical_good = [True] * len(vertical_lines)
    vertical_cnt = len(vertical_lines)
    score = []
    for i in range(len(horizontal_lines)):
        score.append([0] * len(vertical_lines))
    for i in range(len(horizontal_lines)):
        for j in range(len(vertical_lines)):
            score[i][j] = get_cross_diff(img, horizontal_lines[i], vertical_lines[j])
    while horizontal_cnt > inside_lines_cnt or vertical_cnt > inside_lines_cnt:
        horizontal_score = [0] * len(horizontal_lines)
        vertical_score = [0] * len(vertical_lines)
        for i in range(len(horizontal_lines)):
            if not horizontal_good[i]:
                continue
            for j in range(len(vertical_lines)):
                if not vertical_good[j]:
                    continue
                horizontal_score[i] += score[i][j]
                vertical_score[j] += score[i][j]

        worst_horizontal_index = -1
        worst_horizontal_score = float("+inf")
        for i in range(len(horizontal_lines)):
            if not horizontal_good[i]:
                continue
            if worst_horizontal_score > horizontal_score[i]:
                worst_horizontal_index = i
                worst_horizontal_score = horizontal_score[i]
        worst_vertical_index = -1
        worst_vertical_score = float("+inf")

        for j in range(len(vertical_lines)):
            if not vertical_good[j]:
                continue
            if worst_vertical_score > vertical_score[j]:
                worst_vertical_index = j
                worst_vertical_score = vertical_score[j]
        if horizontal_cnt <= inside_lines_cnt:
            vertical_cnt -= 1
            vertical_good[worst_vertical_index] = False
        elif vertical_cnt <= inside_lines_cnt:
            horizontal_cnt -= 1
            horizontal_good[worst_horizontal_index] = False
        else:
            if worst_vertical_score < worst_horizontal_score:
                vertical_cnt -= 1
                vertical_good[worst_vertical_index] = False
            else:
                horizontal_cnt -= 1
                horizontal_good[worst_horizontal_index] = False
    inner_vertical = []
    inner_horizontal = []
    for i in range(len(horizontal_lines)):
        if horizontal_good[i]:
            inner_horizontal.append(horizontal_lines[i])
    for j in range(len(vertical_lines)):
        if vertical_good[j]:
            inner_vertical.append(vertical_lines[j])

    return [inner_horizontal, inner_vertical, horizontal_lines, vertical_lines, horizontal_angles, vertical_angles]


def get_approach(src):
    height, width = src.shape[:2]
    # print("heigth =", height)
    # print("width =", width)
    dst = cv2.Canny(src, 50, 200, None, 3)
    cdst = cv2.cvtColor(dst, cv2.COLOR_GRAY2BGR)
    cdstP = np.copy(cdst)

    linesP = cv2.HoughLinesP(dst, 1, np.pi / 180, 50, None, 50, 10)
    lines = []

    if linesP is not None:
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            cv2.line(cdstP, (l[0], l[1]), (l[2], l[3]), (0, 0, 255), 1, cv2.LINE_AA)
            ln = line_from_segment(Segment(Vector(l[0], l[1]), Vector(l[2], l[3])))
            lines.append(ln)

    start_lines = lines.copy()

    inner_lines = find_inner_lines(src, lines)

    move_delta = 8
    move_cnt = 10
    lines = []
    for ln1 in inner_lines[0]:
        for j in range(move_cnt):
            lines.append(ln1.move(-move_delta * j))
            lines.append(ln1.move(move_delta * j))
    for ln1 in inner_lines[1]:
        for j in range(move_cnt):
            lines.append(ln1.move(-move_delta * j))
            lines.append(ln1.move(move_delta * j))
    inner_lines = find_inner_lines(src, lines, 12)
    lines = []
    for line in start_lines:
        lines.append(line)
    for line in inner_lines[0]:
        lines.append(line)
    for line in inner_lines[1]:
        lines.append(line)
    for line in inner_lines[2]:
        lines.append(line)
    for line in inner_lines[3]:
        lines.append(line)
    inner_lines = find_inner_lines(src, lines, BOARD_LINES_CNT)
    left = []
    right = []
    up = []
    down = []
    for ln in inner_lines[0]:
        left.append(ln.cross(line_from_segment(Segment(Vector(0, 0), Vector(0, 2*height-1)))).y)
        right.append(ln.cross(line_from_segment(Segment(Vector(width-1, 0), Vector(width-1, 2*height-1)))).y)
        # print(ln)
    for ln in inner_lines[1]:
        up.append(ln.cross(line_from_segment(Segment(Vector(0, 0), Vector(width-1, 0)))).x)
        down.append(ln.cross(line_from_segment(Segment(Vector(0, height-1), Vector(width-1, height-1)))).x)
        # print(ln)
    best_board = Board(left, right, up, down, src)
    # best_score = calc_score(best_board)
    # for i in range(20):
    #     board = InnerBoard(random.sample(inner_lines[1], BOARD_LINES_CNT), random.sample(inner_lines[0], BOARD_LINES_CNT))
    #     score = calc_score(best_board, src)
    #     print("score =", score)
    #     if (score > best_score):
    #         best_score = score
    #         best_board = board
    # print("best_score =", best_score)
    return best_board
