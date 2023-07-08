//
// Created by nikita on 03.07.2023.
//

#include "geometry.h"

#include <cmath>

namespace geometry {

    const float EPS = 1e-6;

    Vector::Vector() = default;

    Vector::Vector(float x, float y) : x(x), y(y) {}

    float Vector::length() const {
        return sqrt(x * x + y * y);
    }

    Vector Vector::normalize() const {
        return Vector(x / length(), y / length());
    }

    Vector Vector::rotate(float angle) const {
        return Vector(x * cos(angle) - y * sin(angle), x * sin(angle) + y * cos(angle));
    }

    Vector operator+(Vector v1, Vector v2) {
        return Vector(v1.x + v2.x, v1.y + v2.y);
    }

    Vector operator-(Vector v1, Vector v2) {
        return Vector(v1.x - v2.x, v1.y - v2.y);
    }

    Vector operator*(float value, Vector vec) {
        return Vector(vec.x * value, vec.y * value);
    }

    Vector operator*(Vector vec, float value) {
        return Vector(vec.x * value, vec.y * value);
    }

    Vector operator/(float value, Vector vec) {
        return Vector(vec.x / value, vec.y / value);
    }

    Vector operator/(Vector vec, float value) {
        return Vector(vec.x / value, vec.y / value);
    }

    Segment::Segment() = default;

    Segment::Segment(geometry::Vector pt1, geometry::Vector pt2) : pt1(pt1), pt2(pt2) {}

    Segment::Segment(float x1, float y1, float x2, float y2) : pt1(Vector(x1, y1)), pt2(Vector(x2, y2)) {}

    Line::Line() = default;

    Line::Line(float a, float b, float c) : a(a), b(b), c(c) {}

    Line::Line(Segment sg) {
        a = sg.pt1.y - sg.pt2.y;
        b = sg.pt2.x - sg.pt1.x;
        c = -a * sg.pt1.x - b * sg.pt1.y;
    }

    Vector Line::normal() const {
        return Vector(a, b);
    }

    Vector Line::direction() const {
        return Vector(b, -a);
    }

    Line Line::rotate(float angle, geometry::Vector pt) const {
        Vector n = normal().rotate(angle);
        return Line(n.x, n.y, -n.x * pt.x - -n.y * pt.y);
    }

    float Line::func_value(geometry::Vector pt) const {
        return a * pt.x + b * pt.y + c;
    }

    Line Line::move(float distance) const {
        Vector v = normal().normalize() * distance;
        return Line(a, b, c + a * v.x + b * v.y);
    }

    int sgn(float x) {
        if (abs(x) < EPS) return 0;
        if (x < 0) return -1;
        return 1;
    }

    bool is_cross(Line ln1, Line ln2) {
        return (abs(ln1.a * ln2.b - ln2.a * ln1.b) > EPS && abs(ln2.a * ln1.b - ln1.a * ln2.b) > EPS);
    }

    bool is_cross(Line ln, Segment sg) {
        return (sgn(ln.func_value(sg.pt1)) * sgn(ln.func_value(sg.pt2)) > 0);
    }

    Vector cross(Line ln1, Line ln2) {
//        std::cout << ln1.a << "*x+" << ln1.b << "*y+" << ln1.c << "=0" << std::endl;
//        std::cout << ln2.a << "*x+" << ln2.b << "*y+" << ln2.c << "=0" << std::endl;
        float x = (ln1.b * ln2.c - ln2.b * ln1.c) / (ln1.a * ln2.b - ln2.a * ln1.b);
        float y = (ln2.c * ln1.a - ln1.c * ln2.a) / (ln2.a * ln1.b - ln1.a * ln2.b);
//        std::cout << "(" << x << ", " << y << std::endl;
        return Vector(x, y);
    }

    Vector cross(Line ln, Segment sg) {
        return cross(ln, Line(sg));
    }

    float dist(Vector pt1, Vector pt2) {
        float dx = pt1.x - pt2.x;
        float dy = pt1.y - pt2.y;
        return sqrt(dx * dx + dy * dy);
    }

//    Segment window_segment(int w, int h, Line ln);
//
//    float smooth_distance(int w, int h, Line ln1, Line ln2);
//
//    bool inside_window(int w, int h, int x, int y);


}