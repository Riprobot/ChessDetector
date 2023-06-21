import math
import cv2
import numpy as np
import random as rnd
from image_transforms import four_point_transform, plot_grid_on_transformed_image


def distance(x, y):
    return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def filter_neighbours(arr, eps=math.sqrt(17)):
    if len(arr) == 0:
        return arr
    new_arr = [arr[0]]
    for i in range(1, len(arr)):
        if distance(new_arr[-1], arr[i]) < eps:
            continue
        new_arr.append(arr[i])
    return new_arr


def pixel_dist(pix1, pix2):
    return abs(pix1[0] - pix2[0]) + abs(pix1[1] - pix2[1]) + abs(pix1[2] - pix2[2])


def get_point_error_line(img, point, axis=0, eps=3):
    w, h = img.size[0], img.size[1]
    if axis == 0:
        return pixel_dist(img.getpixel((min(w, int(point[0] + eps)), int(point[1]))),
                          img.getpixel((max(0, int(point[0] - eps)), int(point[1]))))
    else:
        return pixel_dist(img.getpixel((int(point[0]), min(h, int(point[1] + eps)))),
                          img.getpixel((int(point[0]), max(0, int(point[1] - eps)))))


def get_point_error_angle(img, point, eps=3):
    w, h = img.size[0], img.size[1]
    sum1 = pixel_dist(img.getpixel((min(w, int(point[0] + eps)), max(0, int(point[1] - eps)))),
                      img.getpixel((max(0, int(point[0] - eps)), min(h, int(point[1] + eps)))))
    sum2 = pixel_dist(
        img.getpixel((max(0, int(point[0] - eps)), max(0, int(point[1] - eps)))),
        img.getpixel((min(w, int(point[0] + eps)), min(h, int(point[1] + eps)))))
    return sum1 + sum2


def calc_corner_metric(img, corners):
    transformed_image, M = four_point_transform(img, corners)
    ptsT, ptsL = plot_grid_on_transformed_image(transformed_image, draw=False)
    error = 0
    # print(ptsT)
    # print(ptsL)
    for i in range(1, len(ptsT) - 1):
        for j in range(1, len(ptsL) - 1):
            error += get_point_error_line(transformed_image, ((ptsT[i][0] + ptsT[i - 1][0]) / 2, ptsL[j][1]), axis=1)
            error += get_point_error_line(transformed_image, ((ptsT[i][0] * 2 + ptsT[i - 1][0]) / 3, ptsL[j][1]),
                                          axis=1)
            error += get_point_error_line(transformed_image, ((ptsT[i][0] + ptsT[i - 1][0] * 2) / 3, ptsL[j][1]),
                                          axis=1)
    # for i in range(1, len(ptsT) - 1):
    #     for j in range(1, len(ptsL) - 1):
    #         error -= get_point_error_angle(transformed_image, (ptsT[i][0], ptsL[j][1]))
    for i in range(1, len(ptsT) - 1):
        for j in range(1, len(ptsL) - 1):
            error += get_point_error_line(transformed_image, (ptsT[i][0], (ptsL[j][1] + ptsL[j - 1][1]) / 2), axis=0)
            error += get_point_error_line(transformed_image, (ptsT[i][0], (ptsL[j][1] * 2 + ptsL[j - 1][1]) / 3),
                                          axis=0)
            error += get_point_error_line(transformed_image, (ptsT[i][0], (ptsL[j][1] + ptsL[j - 1][1] * 2) / 3),
                                          axis=0)
    return error


def find_corners(img, corner_threshold=0.01):
    w = img.shape[0]
    h = img.shape[1]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    gray = np.float32(gray)
    dst = cv2.cornerHarris(gray, 2, 3, 0.04)

    # result is dilated for marking the corners, not important
    dst = cv2.dilate(dst, None)
    # Threshold for an optimal value, it may vary depending on the image.
    mx = dst.max()
    UL = []
    UR = []
    BL = []
    BR = []
    for x in range(w):
        for y in range(h):
            if dst[x, y] > corner_threshold * mx:
                UL.append((x, y))
                UR.append((x, y))
                BL.append((x, y))
                BR.append((x, y))
    UL = filter_neighbours(sorted(UL, key=lambda x: distance((0, 0), x)))
    UR = filter_neighbours(sorted(UR, key=lambda x: distance((0, h), x)))
    BL = filter_neighbours(sorted(BL, key=lambda x: distance((w, 0), x)))
    BR = filter_neighbours(sorted(BR, key=lambda x: distance((w, h), x)))
    # img[UL[0],UL[1]]=[0,0,255]
    # img[UR[0],UR[1]]=[0,0,255]
    # img[BL[0],BL[1]]=[0,0,255]
    # img[BR[0],BR[1]]=[0,0,255]
    # img[dst > corner_threshold * mx] = [0,0,255]
    # cv2.imwrite( 'test.jpg', img)
    # transformed_image = four_point_transform(filename, np.array([BR, BL, UL, UR]))
    # transformed_image.show()
    best_corner = np.array([UL[0], UR[0], BL[0], BR[0]])[:, ::-1]
    best_value = calc_corner_metric(img, best_corner)
    for i in range(min(len(UL), 10)):
        for j in range(min(len(UR), 10)):
            for k in range(min(len(BL), 10)):
                for l in range(min(len(BR), 10)):
                    new_corner = np.array([UL[i], UR[j], BL[k], BR[l]])[:, ::-1]
                    value = calc_corner_metric(img, new_corner)
                    if value > best_value:
                        best_value = value
                        best_corner = new_corner
    return best_corner


def random_corrector(img, corners, delta=3, max_iter=1000, update_corners=True, save_UL=False, save_UR=False,
                     save_BL=False, save_BR=False):
    w = img.shape[0]
    h = img.shape[1]
    best_corner = corners
    best_value = calc_corner_metric(img, corners)
    for iter in range(max_iter):
        UL_x = corners[2][0] + rnd.randint(-delta, delta) * (not save_UL)
        UL_y = corners[2][1] + rnd.randint(-delta, delta) * (not save_UL)
        UR_x = corners[3][0] + rnd.randint(-delta, delta) * (not save_UR)
        UR_y = corners[3][1] + rnd.randint(-delta, delta) * (not save_UR)
        BL_x = corners[1][0] + rnd.randint(-delta, delta) * (not save_BL)
        BL_y = corners[1][1] + rnd.randint(-delta, delta) * (not save_BL)
        BR_x = corners[0][0] + rnd.randint(-delta, delta) * (not save_BR)
        BR_y = corners[0][1] + rnd.randint(-delta, delta) * (not save_BR)
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


def detect_corners(img=None, img_filename=None, random_correction=True):
    if img is None:
        if img_filename is None:
            return AttributeError("img or img_filename must be not None")
        img = cv2.imread(img_filename)
    corners = find_corners(img)
    if random_correction:
        corners = random_corrector(img, corners)
        corners = random_corrector(img, corners, delta=30, max_iter=1000)
        pass
    transformed_image, M = four_point_transform(img, corners)
    ptsT, ptsL = plot_grid_on_transformed_image(transformed_image, draw=True)
    return corners
