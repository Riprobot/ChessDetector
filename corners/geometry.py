import math

EPS = 1e-6

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f'({self.x}, {self.y})'

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, value):
        return Vector(self.x * value, self.y * value)

    def __rmul__(self, value):
        return Vector(self.x * value, self.y * value)

    def __truediv__(self, value):
        return Vector(self.x / value, self.y / value)

    def __rtruediv__(self, value):
        return Vector(self.x / value, self.y / value)

    def length(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def normalize(self):
        return self / self.length()

    def rotate(self, angle):
        return Vector(self.x * math.cos(angle) - self.y * math.sin(angle),
                      self.x * math.sin(angle) + self.y * math.cos(angle))


class Segment:
    def __init__(self, pt1, pt2):
        self.pt1 = pt1
        self.pt2 = pt2


class Line:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    def __str__(self):
        return f'{self.a} * x + {self.b} * y + {self.c} = 0'

    def rotate(self, angle, pt):
        v = self.normal().rotate(angle)
        a = v.x
        b = v.y
        c = -a * pt.x - b * pt.y
        return Line(a, b, c)

    def normal(self):
        return Vector(self.a, self.b)

    def direction(self):
        return Vector(self.b, -self.a)

    def func_value(self, pt):
        return self.a * pt.x + self.b * pt.y + self.c

    def move(self, distance):
        move_vector = self.normal().normalize() * distance
        return Line(self.a, self.b, self.c + self.a * move_vector.x + self.b * move_vector.y)

    def cross(self, other):
        if type(other) == Line:
            a1, b1, c1 = self.a, self.b, self.c
            a2, b2, c2 = other.a, other.b, other.c
            if abs(a1 * b2 - a2 * b1) < EPS or abs(a2 * b1 - a1 * b2) < EPS:
                return None
            return Vector((b1 * c2 - b2 * c1) / (a1 * b2 - a2 * b1), (c2 * a1 - c1 * a2) / (a2 * b1 - a1 * b2))
        elif type(other) == Segment:
            # print("cross", self, other.pt1, other.pt2)
            if self.func_value(other.pt1) > 0 and self.func_value(other.pt2) > 0:
                # print("NONE")
                return None
            if self.func_value(other.pt1) < 0 and self.func_value(other.pt2) < 0:
                # print("NONE")
                return None
            #
            # if self.func_value(other.pt1) * self.func_value(other.pt2) > EPS:
            #     return None
            return self.cross(line_from_segment(other))
        return None


def line_from_segment(segment):
    x1 = segment.pt1.x
    y1 = segment.pt1.y
    x2 = segment.pt2.x
    y2 = segment.pt2.y
    dx = x2 - x1
    dy = y2 - y1
    a = -dy
    b = dx
    c = -a * x1 - b * y1
    return Line(a, b, c)


def dist(pt1, pt2):
    dx = pt1.x - pt2.x
    dy = pt1.y - pt2.y
    return math.sqrt(dx * dx + dy * dy)


def get_window_segment(w, h, ln):
    edges = [Segment(Vector(0, 0), Vector(w-1, 0)), Segment(Vector(w-1, 0), Vector(w-1, h-1)),
             Segment(Vector(w-1, h-1), Vector(0, h-1)), Segment(Vector(0, h-1), Vector(0, 0))]
    points = []
    for edge in edges:
        pt = ln.cross(edge)
        if pt is not None:
            points.append(pt)
    if len(points) == 2:
        return Segment(points[0], points[1])
    return None


def smooth_distance(w, h, ln1, ln2):
    sg1 = get_window_segment(w, h, ln1)
    sg2 = get_window_segment(w, h, ln2)
    if sg1 is None or sg2 is None:
        return max(w, h)
    dst1 = (dist(sg1.pt1, sg2.pt1) + dist(sg1.pt2, sg2.pt2)) / 2
    dst2 = (dist(sg1.pt2, sg2.pt1) + dist(sg1.pt1, sg2.pt2)) / 2
    return min(dst1, dst2)


def inside_window(w, h, pt):
    return 0 <= pt.x < w and 0 <= pt.y < h


def hash_tuple(w, h, obj):
    accuracy = 10
    if type(obj) == Line:
        return hash_tuple(w, h, get_window_segment(w, h, obj))
    if type(obj) == Segment:
        pt1 = (round(accuracy * obj.pt1.x), round(accuracy * obj.pt1.y))
        pt2 = (round(accuracy * obj.pt2.x), round(accuracy * obj.pt2.y))
        if pt1 < pt2:
            return pt1, pt2
        else:
            return pt2, pt1
    return None
