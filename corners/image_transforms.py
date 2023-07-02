import matplotlib.pyplot as plt
from PIL import Image
from matplotlib.pyplot import figure
from numpy import asarray
import numpy as np
import cv2

# perspective transforms an image with four given corners
def four_point_transform(img, pts):
    image = asarray(img)
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # construct set of destination points to obtain a "birds eye view"
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

    img = Image.fromarray(warped, "RGB")
    # img.show()
    # return the warped image
    return img, M



def order_points(pts):
    # order a list of 4 coordinates:
    # 0: top-left,
    # 1: top-right
    # 2: bottom-right,
    # 3: bottom-left8
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    return rect


def plot_grid_on_transformed_image(image, draw=False):
    corners = np.array([[0, 0],
                        [image.size[0], 0],
                        [0, image.size[1]],
                        [image.size[0], image.size[1]]])

    corners = order_points(corners)

    # im = plt.imread(image)
    if draw:
        figure(figsize=(10, 10), dpi=80)
        plt.imshow(cv2.cvtColor(np.array(image), cv2.COLOR_BGR2RGB))
    TL = corners[0]
    BL = corners[3]
    TR = corners[1]
    BR = corners[2]

    def interpolate(xy0, xy1):
        x0, y0 = xy0
        x1, y1 = xy1
        dx = (x1 - x0) / 8
        dy = (y1 - y0) / 8
        pts = [(x0 + i * dx, y0 + i * dy) for i in range(9)]
        return pts

    ptsT = interpolate(TL, TR)
    ptsL = interpolate(TL, BL)
    ptsR = interpolate(TR, BR)
    ptsB = interpolate(BL, BR)
    if draw:
        for a, b in zip(ptsL, ptsR):
            plt.plot([a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--")
        for a, b in zip(ptsT, ptsB):
            plt.plot([a[0], b[0]], [a[1], b[1]], 'ro', linestyle="--")

        plt.axis('off')
        plt.savefig('temp/chessboard_transformed_with_grid.jpg')
    return ptsT, ptsL

def get_point_by_box(box):
    BL = (box[0], box[1])
    UR = (box[2], box[3])
    return np.array([(BL[0] + UR[0]) / 2, (BL[1] + UR[1] * 3) / 4])


def get_perspective_point(point, M):
    pts = np.array([[point[0], point[1]]], dtype="float32")
    pts = np.array([pts])
    return cv2.perspectiveTransform(pts, M)[0][0]
