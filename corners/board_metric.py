from corners.image_transforms import four_point_transform, plot_grid_on_transformed_image


def pixel_diff(pix1, pix2):
    return (pix1[0] - pix2[0]) + (pix1[1] - pix2[1]) + (pix1[2] - pix2[2])


def pixel_dist(pix1, pix2):
    return abs(pix1[0] - pix2[0]) + abs(pix1[1] - pix2[1]) + abs(pix1[2] - pix2[2])


def get_point_error_line(img, point, axis=0, signed=False, eps=3):
    w, h = img.size[0], img.size[1]
    result = 0
    if axis == 0:
        result = pixel_diff(img.getpixel((min(w - 1, int(point[0] + eps)), int(point[1]))),
                            img.getpixel((max(0, int(point[0] - eps)), int(point[1]))))
    else:
        result = pixel_diff(img.getpixel((int(point[0]), min(h - 1, int(point[1] + eps)))),
                            img.getpixel((int(point[0]), max(0, int(point[1] - eps)))))
    if signed:
        return result
    else:
        return abs(result)


def get_point_error_angle(img, point, eps=3):
    w, h = img.size[0], img.size[1]
    sum1 = pixel_dist(img.getpixel((min(w - 1, int(point[0] + eps)), max(0, int(point[1] - eps)))),
                      img.getpixel((max(0, int(point[0] - eps)), min(h, int(point[1] + eps)))))
    sum2 = pixel_dist(
        img.getpixel((max(0, int(point[0] - eps)), max(0, int(point[1] - eps)))),
        img.getpixel((min(w - 1, int(point[0] + eps)), min(h - 1, int(point[1] + eps)))))
    return sum1 + sum2


def calc_corner_metric(img, corners, draw_flag=False, use_color=True):
    transformed_image, M = four_point_transform(img, corners)
    ptsT, ptsL = plot_grid_on_transformed_image(transformed_image, draw=draw_flag)
    error = 0
    # print(ptsT)
    # print(ptsL)
    # print("len(ptsT), len(ptsL), ", len(ptsT), len(ptsL))
    # print(ptsT, ptsL)
    for i in range(1, len(ptsT) - 1):
        for j in range(1, len(ptsL) - 1):
            sgn = 1
            if (use_color and (i + j) % 2 == 1):
                sgn = -1
            error += sgn * 0.33 * get_point_error_line(transformed_image,
                                                       ((9 * ptsT[i][0] + ptsT[i - 1][0]) / 10, ptsL[j][1]), axis=1,
                                                       signed=use_color)
            error += sgn * 0.33 * get_point_error_line(transformed_image,
                                                       ((ptsT[i][0] + ptsT[i - 1][0] * 9) / 10, ptsL[j][1]), axis=1,
                                                       signed=use_color)
            error += sgn * 0.33 * get_point_error_line(transformed_image,
                                                       ((ptsT[i][0] + ptsT[i - 1][0]) / 2, ptsL[j][1]), axis=1,
                                                       signed=use_color)
            error += sgn * get_point_error_line(transformed_image, ((ptsT[i][0] * 2 + ptsT[i - 1][0]) / 3, ptsL[j][1]),
                                                axis=1, signed=use_color)
            error += sgn * get_point_error_line(transformed_image, ((ptsT[i][0] + ptsT[i - 1][0] * 2) / 3, ptsL[j][1]),
                                                axis=1, signed=use_color)
    for i in range(1, len(ptsT) - 1):
        for j in range(1, len(ptsL) - 1):
            error -= 0.3 * get_point_error_angle(transformed_image, (ptsT[i][0], ptsL[j][1]))
    for i in range(1, len(ptsT) - 1):
        for j in range(1, len(ptsL) - 1):
            sgn = 1
            if (use_color and (i + j) % 2 == 1):
                sgn = -1
            error += sgn * 0.5 * get_point_error_line(transformed_image,
                                                      (ptsT[i][0], (9 * ptsL[j][1] + ptsL[j - 1][1]) / 10), axis=0,
                                                      signed=use_color)
            error += sgn * 0.5 * get_point_error_line(transformed_image,
                                                      (ptsT[i][0], (ptsL[j][1] + ptsL[j - 1][1] * 9) / 10), axis=0,
                                                      signed=use_color)
            error += sgn * 0.33 * get_point_error_line(transformed_image,
                                                       (ptsT[i][0], (ptsL[j][1] + ptsL[j - 1][1]) / 2), axis=0,
                                                       signed=use_color)
            error += sgn * get_point_error_line(transformed_image, (ptsT[i][0], (ptsL[j][1] * 2 + ptsL[j - 1][1]) / 3),
                                                axis=0, signed=use_color)
            error += sgn * get_point_error_line(transformed_image, (ptsT[i][0], (ptsL[j][1] + ptsL[j - 1][1] * 2) / 3),
                                                axis=0, signed=use_color)
    return error
