from corners.geometry import *
import random

BOARD_LINES_CNT = 7

def horizontal_sort_key(ln):
    return ln.cross(Line(1, 0, 0)).y


def vertical_sort_key(ln):
    return ln.cross(Line(0, 1, 0)).x


class Board:
    def __init__(self, left, right, up, down, img):
        self.h, self.w = img.shape[:2]
        self.img = img
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        edge_delta = 10
        for i in range(BOARD_LINES_CNT):
            self.left[i] = max(edge_delta, min(self.h - 1 - edge_delta, round(self.left[i])))
            self.right[i] = max(edge_delta, min(self.h - 1 - edge_delta, round(self.right[i])))
            self.up[i] = max(edge_delta, min(self.w - 1 - edge_delta, round(self.up[i])))
            self.down[i] = max(edge_delta, min(self.w - 1 - edge_delta, round(self.down[i])))
        self.left.sort()
        self.right.sort()
        self.up.sort()
        self.down.sort()
        score_result = calc_score(self, True)
        self.score = score_result[0]
        self.confidence = score_result[1]
        worst_horizontal = 0
        worst_vertical = 0
        for i in range(BOARD_LINES_CNT):
            if score_result[1][0][i] < score_result[1][0][worst_horizontal]:
                worst_horizontal = i
            if score_result[1][1][i] < score_result[1][1][worst_vertical]:
                worst_vertical = i
        self.worst_horizontal = worst_horizontal
        self.worst_vertical = worst_vertical

    def horizontal(self, i):
        return line_from_segment(Segment(Vector(0, self.left[i]), Vector(self.w - 1, self.right[i])))

    def vertical(self, j):
        return line_from_segment(Segment(Vector(self.up[j], 0), Vector(self.down[j], self.h - 1)))

    def get_cross(self, i, j):
        h_ln = line_from_segment(Segment(Vector(0, self.left[i]), Vector(self.w - 1, self.right[i])))
        v_ln = line_from_segment(Segment(Vector(self.up[j], 0), Vector(self.down[j], self.h - 1)))
        return h_ln.cross(v_ln)


segment_value_cache = dict()
cross_value_cache = dict()

segment_statistic = [0, 0]
cross_statistic = [0, 0]


def segment_value(img, sg):
    h, w = img.shape[:2]
    hash_val = hash_tuple(h, w, sg)
    if hash_val in segment_value_cache:
        # segment_statistic[0] += 1
        return segment_value_cache[hash_val]
    # segment_statistic[1] += 1
    h, w = img.shape[:2]
    pt1 = sg.pt1
    pt2 = sg.pt2
    direction = Vector(pt2.x - pt1.x, pt2.y - pt1.y).normalize()
    norm = Vector(direction.y, -direction.x).normalize()
    eps = 3
    cnt = 64
    sm = 0
    cnt = 0
    for i in range(1, cnt):
        x1 = round(pt1.x + direction.x * i + norm.x * eps)
        y1 = round(pt1.y + direction.y * i + norm.y * eps)
        x2 = round(pt1.x + direction.x * i - norm.x * eps)
        y2 = round(pt1.y + direction.y * i - norm.y * eps)
        if 0 <= x1 < w and 0 <= y1 < h and 0 <= x2 < w and 0 <= y2 < h:
            delta = abs(float(img[y1, x1]) - float(img[y2, x2]))
            sm += delta
            cnt += 1
    result = 0
    if cnt != 0:
        result = sm / cnt
    segment_value_cache[hash_val] = result
    return result


def cross_value(img, left, right, up, down):
    h, w = img.shape[:2]
    hash_val = (left, right, up, down)
    if hash_val in cross_value_cache:
        return cross_value_cache[hash_val]
    ln1 = line_from_segment(Segment(Vector(0, left), Vector(w - 1, right)))
    ln2 = line_from_segment(Segment(Vector(up, 0), Vector(down, h - 1)))
    dot = ln1.cross(ln2)
    d1 = ln1.direction().normalize()
    d2 = ln2.direction().normalize()
    radius = 5
    sm = [0, 0, 0, 0]
    cnt = [0, 0, 0, 0]
    for i in range(-radius, radius + 1):
        if i == 0:
            continue
        for j in range(-radius, radius + 1):
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
            if 0 <= x < w and 0 <= y < h:
                pixel_color = img[y, x]
                weight = (1 / min(abs(i), abs(j)))
                sm[index] += pixel_color * weight
                cnt[index] += weight
    for i in range(4):
        if cnt[i] == 0:
            # print("wtf")
            cross_value_cache[hash_val] = -255 * 4
            return -255 * 4
    color = [(sm[0] / cnt[0]), (sm[1] / cnt[1]), (sm[2] / cnt[2]), (sm[3] / cnt[3])]
    result = 0
    for i in range(4):
        result += abs(color[i] - color[(i + 1) % 4])
    result -= 2 * abs(color[0] - color[2])
    result -= 2 * abs(color[1] - color[3])
    cross_value_cache[hash_val] = result
    return result


def calc_score(board, get_confidence=False):
    confidence = [[0] * BOARD_LINES_CNT, [0] * BOARD_LINES_CNT]
    result = 0
    for i in range(BOARD_LINES_CNT - 1):
        result -= 100 / max(0.001, board.up[i + 1] - board.up[i])
        result -= 100 / max(0.001, board.down[i + 1] - board.down[i])
        result -= 100 / max(0.001, board.left[i + 1] - board.left[i])
        result -= 100 / max(0.001, board.right[i + 1] - board.right[i])

    cross_result = 0
    for i in range(BOARD_LINES_CNT):
        for j in range(BOARD_LINES_CNT):
            val = cross_value(board.img, board.left[i], board.right[i], board.up[j], board.down[j])
            confidence[0][i] += val
            confidence[1][j] += val
            cross_result += val
    segment_result = 0
    for i in range(BOARD_LINES_CNT):
        pt1 = board.get_cross(i, 0)
        pt2 = board.get_cross(i, BOARD_LINES_CNT - 1)
        dir_vec = pt2 - pt1
        dir_vec = dir_vec / (BOARD_LINES_CNT - 1)
        pt2 = pt2 + dir_vec
        pt1 = pt1 - dir_vec
        sg_val = segment_value(board.img, Segment(pt1, pt2))
        confidence[0][i] += sg_val
        segment_result += sg_val
    for i in range(BOARD_LINES_CNT):
        pt1 = board.get_cross(0, i)
        pt2 = board.get_cross(BOARD_LINES_CNT - 1, i)
        dir_vec = pt2 - pt1
        dir_vec = dir_vec / (BOARD_LINES_CNT - 1)
        pt2 = pt2 + dir_vec
        pt1 = pt1 - dir_vec
        sg_val = segment_value(board.img, Segment(pt1, pt2))
        confidence[1][i] += sg_val
        segment_result += sg_val

    form_result = 0
    for i in range(BOARD_LINES_CNT - 1):
        for j in range(BOARD_LINES_CNT - 1):
            h = (dist(board.get_cross(i, j), board.get_cross(i, j + 1)) + dist(board.get_cross(i + 1, j),
                                                                               board.get_cross(i + 1, j + 1))) / 2
            w = (dist(board.get_cross(i, j), board.get_cross(i + 1, j)) + dist(board.get_cross(i, j + 1),
                                                                               board.get_cross(i + 1, j + 1))) / 2
            ratio = abs(h - w) / max(1, max(h, w))
            form_result -= max(0, ratio - 0.2) * 1000
    result += cross_result
    result += 1 * form_result
    result += 2 * segment_result
    # print("###", result)
    if get_confidence:
        return [result, confidence]
    return result


def random_choice(a):
    r = random.randint(0, sum(a) - 1)
    index = 0
    while r >= a[index]:
        r -= a[index]
        index += 1
    return index


def transform(board):
    h = board.h
    w = board.w
    new_left = board.left.copy()
    new_right = board.right.copy()
    new_up = board.up.copy()
    new_down = board.down.copy()
    chance_weight = [100, 100, 100, 100, 50, 100, 50]
    # 0 - change_to_random
    # 1 - small parallel move
    # 2 - big parallel move
    # 3 - change to average
    # 4 - swap begin end
    # 5 - small rotate
    # 6 - create new_average
    transform_index = random_choice(chance_weight)
    worst_chance = 0.3
    if transform_index == 0:
        if random.random() < 0.5:
            # horizontal
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_horizontal
            if i == 0:
                new_left[i] = random.triangular(new_left[i] - (new_left[i + 1] - new_left[i]), new_left[i + 1] - 1,
                                                new_left[i])
                new_right[i] = random.triangular(new_right[i] - (new_right[i + 1] - new_right[i]), new_right[i + 1] - 1,
                                                 new_right[i])
            elif i == BOARD_LINES_CNT - 1:
                new_left[i] = random.triangular(new_left[i - 1] + 1, new_left[i] + (new_left[i] - new_left[i - 1]),
                                                new_left[i])
                new_right[i] = random.triangular(new_right[i - 1] + 1, new_right[i] + (new_right[i] - new_right[i - 1]),
                                                 new_right[i])
            else:
                new_left[i] = random.triangular(new_left[i - 1] + 1, new_left[i + 1] - 1, new_left[i])
                new_right[i] = random.triangular(new_right[i - 1] + 1, new_right[i + 1] - 1, new_right[i])
        else:
            # vertical
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_vertical
            if i == 0:
                new_up[i] = random.triangular(new_up[i] - (new_up[i + 1] - new_up[i]), new_up[i + 1] - 1, new_up[i])
                new_down[i] = random.triangular(new_down[i] - (new_down[i + 1] - new_down[i]), new_down[i + 1] - 1,
                                                new_down[i])
            elif i == BOARD_LINES_CNT - 1:
                new_up[i] = random.triangular(new_up[i - 1] + 1, new_up[i] + (new_up[i] - new_up[i - 1]), new_up[i])
                new_down[i] = random.triangular(new_down[i - 1] + 1, new_down[i] + (new_down[i] - new_down[i - 1]),
                                                new_down[i])
            else:
                new_up[i] = random.triangular(new_up[i - 1] + 1, new_up[i + 1] - 1, new_up[i])
                new_down[i] = random.triangular(new_down[i - 1] + 1, new_down[i + 1] - 1, new_down[i])
    if transform_index == 1:
        if random.random() < 0.5:
            # horizontal
            min_distance = -80
            max_distance = 80
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_horizontal
            if i != 0:
                min_distance = max(min_distance, new_left[i - 1] - new_left[i])
                min_distance = max(min_distance, new_right[i - 1] - new_right[i])
            if i != BOARD_LINES_CNT - 1:
                max_distance = min(max_distance, new_left[i + 1] - new_left[i])
                max_distance = min(max_distance, new_right[i + 1] - new_right[i])
            distance = random.triangular(min_distance, max_distance)
            new_left[i] += distance
            new_right[i] += distance
        else:
            # vertical
            min_distance = -80
            max_distance = 80
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_vertical
            if i != 0:
                min_distance = max(min_distance, new_up[i - 1] - new_up[i])
                min_distance = max(min_distance, new_down[i - 1] - new_down[i])
            if i != BOARD_LINES_CNT - 1:
                max_distance = min(max_distance, new_up[i + 1] - new_up[i])
                max_distance = min(max_distance, new_down[i + 1] - new_down[i])
            distance = random.triangular(min_distance, max_distance)
            new_up[i] += distance
            new_down[i] += distance
    if transform_index == 2:
        if random.random() < 0.5:
            # horizontal
            min_distance = -160
            max_distance = 160
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_horizontal
            min_distance = max(min_distance, 0 - new_left[i])
            min_distance = max(min_distance, 0 - new_right[i])
            max_distance = min(max_distance, (h - 1) - new_left[i])
            max_distance = min(max_distance, (h - 1) - new_right[i])
            distance = random.triangular(min_distance, max_distance)
            new_left[i] += distance
            new_right[i] += distance
        else:
            # vertical
            min_distance = -160
            max_distance = 160
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_vertical
            min_distance = max(min_distance, 0 - new_up[i])
            min_distance = max(min_distance, 0 - new_down[i])
            max_distance = min(max_distance, (h - 1) - new_up[i])
            max_distance = min(max_distance, (h - 1) - new_down[i])
            distance = random.triangular(min_distance, max_distance)
            new_up[i] += distance
            new_down[i] += distance
    if transform_index == 3:
        if random.random() < 0.5:
            # horizontal
            i = random.randint(1, BOARD_LINES_CNT - 2)
            new_left[i] = (new_left[i - 1] + new_left[i + 1]) / 2 + random.triangular(-5, 5)
            new_right[i] = (new_right[i - 1] + new_right[i + 1]) / 2 + random.triangular(-5, 5)
        else:
            # vertical
            i = random.randint(1, BOARD_LINES_CNT - 2)
            new_up[i] = (new_up[i - 1] + new_up[i + 1]) / 2 + random.triangular(-5, 5)
            new_down[i] = (new_down[i - 1] + new_down[i + 1]) / 2 + random.triangular(-5, 5)
    if transform_index == 4:
        if random.random() < 0.5:
            if random.random() < 0.5:
                # new_left[BOARD_LINES_CNT - 1] = new_left[0] + (
                #         new_left[BOARD_LINES_CNT - 2] - new_left[BOARD_LINES_CNT - 1]) + random.triangular(-5, 5)
                # new_right[BOARD_LINES_CNT - 1] = new_right[0] + (
                #         new_right[BOARD_LINES_CNT - 2] - new_right[BOARD_LINES_CNT - 1]) + random.triangular(-5, 5)
                new_left[BOARD_LINES_CNT - 1] = new_left[0] + (new_left[0] - new_left[1]) + random.triangular(-5, 5)
                new_right[BOARD_LINES_CNT - 1] = new_right[0] + (new_right[0] - new_right[1]) + random.triangular(-5, 5)
            else:
                # new_left[0] = new_left[BOARD_LINES_CNT - 1] + (new_left[1] - new_left[0]) + random.triangular(-5, 5)
                # new_right[0] = new_right[BOARD_LINES_CNT - 1] + (new_right[1] - new_right[0]) + random.triangular(-5, 5)
                new_left[0] = new_left[BOARD_LINES_CNT - 1] + (new_left[BOARD_LINES_CNT - 1] - new_left[BOARD_LINES_CNT - 2]) + random.triangular(-5, 5)
                new_right[0] = new_right[BOARD_LINES_CNT - 1] + (new_right[BOARD_LINES_CNT - 1] - new_right[BOARD_LINES_CNT - 2]) + random.triangular(-5, 5)
        else:
            if random.random() < 0.5:
                # new_up[BOARD_LINES_CNT - 1] = new_up[0] + (new_up[BOARD_LINES_CNT - 2] - new_up[BOARD_LINES_CNT - 1]) + random.triangular(-5, 5)
                # new_down[BOARD_LINES_CNT - 1] = new_down[0] + (new_down[BOARD_LINES_CNT - 2] - new_down[BOARD_LINES_CNT - 1]) + random.triangular(-5, 5)
                new_up[BOARD_LINES_CNT - 1] = new_up[0] + (new_up[0] - new_up[1]) + random.triangular(-5, 5)
                new_down[BOARD_LINES_CNT - 1] = new_down[0] + (new_down[0] - new_down[1]) + random.triangular(-5, 5)
            else:
                new_up[0] = new_up[BOARD_LINES_CNT - 1] + (new_up[BOARD_LINES_CNT - 1] - new_up[BOARD_LINES_CNT - 2]) + random.triangular(-5, 5)
                new_down[0] = new_down[BOARD_LINES_CNT - 1] + (new_down[BOARD_LINES_CNT - 1] - new_down[BOARD_LINES_CNT - 2]) + random.triangular(-5, 5)
    if transform_index == 5:
        if random.random() < 0.5:
            # horizontal
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_horizontal
            new_left[i] = new_left[i] + random.triangular(-5, 5)
            new_right[i] = new_right[i] + random.triangular(-5, 5)
        else:
            # vertical
            i = random.randint(0, BOARD_LINES_CNT - 1)
            if random.random() < worst_chance:
                i = board.worst_vertical
            new_up[i] = new_up[i] + random.triangular(-5, 5)
            new_down[i] = new_down[i] + random.triangular(-5, 5)
    if transform_index == 6:
        if random.random() < 0.5:
            a = []
            for i in range(1, BOARD_LINES_CNT - 3):
                val = new_left[i + 1] - new_left[i] + new_right[i + 1] - new_right[i]
                a.append(val * val)
            i = random_choice(a) + 1
            replace_index = 0
            if random.random() < 0.5:
                replace_index = BOARD_LINES_CNT - 1
            if (board.worst_horizontal == 0 or board.worst_horizontal == BOARD_LINES_CNT - 1) and random.random() < 0.7:
                replace_index = board.worst_horizontal
            new_left[replace_index] = (new_left[i - 1] + new_left[i + 1]) / 2 + random.triangular(-5, 5)
            new_right[replace_index] = (new_right[i - 1] + new_right[i + 1]) / 2 + random.triangular(-5, 5)
        else:
            a = []
            for i in range(1, BOARD_LINES_CNT - 3):
                val = new_up[i + 1] - new_up[i] + new_down[i + 1] - new_down[i]
                a.append(val * val)
            i = random_choice(a) + 1
            replace_index = 0
            if random.random() < 0.5:
                replace_index = BOARD_LINES_CNT - 1
            if (board.worst_vertical == 0 or board.worst_vertical == BOARD_LINES_CNT - 1) and random.random() < 0.7:
                replace_index = board.worst_vertical
            new_up[replace_index] = (new_up[i - 1] + new_up[i + 1]) / 2 + random.triangular(-5, 5)
            new_down[replace_index] = (new_down[i - 1] + new_down[i + 1]) / 2 + random.triangular(-5, 5)
    return Board(new_left, new_right, new_up, new_down, board.img)


def probability(old_score, new_score, temperature):
    # print("!", new_score, old_score)
    if new_score > old_score:
        return 1
    return math.exp((new_score - old_score) / temperature)


def simulation(board):
    ITER_CNT = 6000
    START_T = 100
    for i in range(ITER_CNT):
        t = START_T - (i * START_T / ITER_CNT)
        new_board = transform(board)
        if random.random() <= probability(board.score, new_board.score, t):
            board = new_board
        # if i % 100 == 0:
        #     cross_value_cache.clear()
        #     segment_value_cache.clear()
        # if i % 100 == 0:
        #     print("score =", board.score, "i =", i, "t=", t)
    for i in range(100):
        t = 1
        new_board = transform(board)
        if random.random() <= probability(board.score, new_board.score, t):
            board = new_board
    # print("final_score=", board.score)
    # print("cross_stat=", cross_statistic[0] / sum(cross_statistic), cross_statistic)
    # print("segment_stat=", segment_statistic[0] / sum(segment_statistic), segment_statistic)
    return board
