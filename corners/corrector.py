import numpy as np
from corners.board_metric import calc_corner_metric
import random

def random_corrector(img, corners, delta=3, max_iter=1000, update_corners=True, save_UL=False, save_UR=False,
                     save_BL=False, save_BR=False):
    w = img.shape[0]
    h = img.shape[1]
    best_corner = corners
    best_value = calc_corner_metric(img, corners)
    for iter in range(max_iter):
        UL_x = corners[2][0] + random.randint(-delta, delta) * (not save_UL)
        UL_y = corners[2][1] + random.randint(-delta, delta) * (not save_UL)
        UR_x = corners[3][0] + random.randint(-delta, delta) * (not save_UR)
        UR_y = corners[3][1] + random.randint(-delta, delta) * (not save_UR)
        BL_x = corners[1][0] + random.randint(-delta, delta) * (not save_BL)
        BL_y = corners[1][1] + random.randint(-delta, delta) * (not save_BL)
        BR_x = corners[0][0] + random.randint(-delta, delta) * (not save_BR)
        BR_y = corners[0][1] + random.randint(-delta, delta) * (not save_BR)
        UL_x = min(max(0, UL_x), w)
        UL_y = min(max(0, UL_y), h)
        UR_x = min(max(0, UR_x), w)
        UR_y = min(max(0, UR_y), h)
        BL_x = min(max(0, BL_x), w)
        BL_y = min(max(0, BL_y), h)
        BR_x = min(max(0, BR_x), w)
        BR_y = min(max(0, BR_y), h)
        new_corner = np.array([[UL_x, UL_y], [UR_x, UR_y], [BL_x, BL_y], [BR_x, BR_y]])
        value = calc_corner_metric(img, new_corner)
        if value > best_value:
            best_value = value
            best_corner = new_corner
            if update_corners:
                corners = best_corner
    return best_corner
