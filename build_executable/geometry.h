//
// Created by nikita on 03.07.2023.
//

#ifndef BOARD_FINDER_CALC_GEOMETRY_H
#define BOARD_FINDER_CALC_GEOMETRY_H

namespace geometry {
    struct Vector {
        Vector();

        Vector(float x, float y);

        float length() const;

        Vector normalize() const;

        Vector rotate(float angle) const;

        float x = 0;
        float y = 0;
    };

    Vector operator+(Vector v1, Vector v2);

    Vector operator-(Vector v1, Vector v2);

    Vector operator*(float value, Vector vec);

    Vector operator*(Vector vec, float value);

    Vector operator/(float value, Vector vec);

    Vector operator/(Vector vec, float value);

    struct Segment {
        Segment();

        Segment(Vector pt1, Vector pt2);

        Segment(float x1, float y1, float x2, float y2);

        Vector pt1;
        Vector pt2;
    };

    struct Line {
        Line();

        Line(float a, float b, float c);

        Line(Segment sg);

        Vector normal() const;

        Vector direction() const;

        Line rotate(float angle, Vector pt) const;

        float func_value(Vector pt) const;

        Line move(float distance) const;

        float a = 0;
        float b = 0;
        float c = 0;
    };

    bool is_cross(Line ln1, Line ln2);

    bool is_cross(Line ln, Segment sg);

    Vector cross(Line ln1, Line ln2);

    Vector cross(Line ln, Segment sg);

    float dist(Vector pt1, Vector pt2);

//    Segment window_segment(int w, int h, Line ln);
//
//    float smooth_distance(int w, int h, Line ln1, Line ln2);
//
//    bool inside_window(int w, int h, int x, int y);

}

#include "geometry.cpp"

#endif //BOARD_FINDER_CALC_GEOMETRY_H
