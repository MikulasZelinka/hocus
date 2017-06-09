from math import pi, cos, sin, sqrt
from itertools import combinations

import cairo

# A4
HEIGHT, WIDTH = 8.3 * 72, 11.7 * 72


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    def __add__(self, b):
        return Point(self.x + b.x, self.y + b.y)

    def __sub__(self, b):
        return Point(self.x - b.x, self.y - b.y)

    def __mul__(self, c):
        return Point(self.x * c, self.y * c)

    def __iter__(self):
        yield self.x
        yield self.y

    def rotated(self, alpha, around=None):
        if not around:
            around = Point(0, 0)
        x = self.x - around.x
        y = self.y - around.y
        return Point(
            cos(alpha) * x - sin(alpha) * y,
            sin(alpha) * x + cos(alpha) * y
        ) + around
        return

    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def dist(self, q):
        return (self - q).norm()


class HocusContext(cairo.Context):

    # distance between two edges of a connecting link in the 2D projection
    width = 10

    # distance from the middle of a cube to one of its vertices in the 2D
    # projection
    edge = width / cos(pi / 6)

    def draw_point(self, p):
        """Draw cross at p"""
        self.set_line_width(1)
        self.set_source_rgba(0, 0, 0, 1)
        self.move_to(p.x + 10, p.y)
        self.line_to(p.x - 10, p.y)
        self.stroke()
        self.move_to(p.x, p.y + 10)
        self.line_to(p.x, p.y - 10)
        self.stroke()

    def draw_line(self, p, q, line_width=2, line_cap=cairo.LINE_CAP_ROUND):
        """Draw line between p and q"""
        self.set_line_width(line_width)
        self.set_line_cap(line_cap)
        self.move_to(*p)
        self.line_to(*q)
        self.stroke()

    def draw_cube(self, middle, edges):

        edges = set(e - 1 for e in edges)
        top = middle - Point(0, self.edge)

        # No comment would help you. Draw it.
        for i in range(3):
            if i * 2 not in edges and ((i + 1) * 2) % 6 not in edges:
                self.draw_line(
                    middle,
                    top.rotated((1 + 2 * i) * pi / 3, middle)
                )
            if i * 2 in edges:
                self.draw_line(middle, top.rotated(2 * i * pi / 3, middle))

        for i in range(6):
            if not (i in edges or (i + 1) % 6 in edges):
                self.draw_line(
                    top.rotated(i * pi / 3, middle),
                    top.rotated((i + 1) * pi / 3, middle)
                )

    def draw_link(self, p, q):
        """Draw connection between two cubes"""
        self.draw_line(p, q)

        # outer lines are shorter so that they don't cross with neighbouring
        # ones
        r = (p - q.rotated(pi / 3, p)) * (self.edge / p.dist(q))
        r2 = (p - r).rotated(-2 * pi / 3, p) - p
        self.draw_line(p - r, q - r2)
        self.draw_line(p + r2, q + r)


def visualise(binary, paths, filename):
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    cr = HocusContext(surface)

    def test_vis():
        """Draw all possible cases"""
        for i in range(7):
            for j, e in enumerate(combinations(range(1, 7), i)):
                cr.draw_cube(50 * (j + 1), 50 * (i + 1), e)

    p = Point(100, 100)
    q = (p + Point(0, 100)).rotated(- pi / 3, Point(100, 100))
    r = q + Point(0, 100)
    cr.draw_cube(p, [3])
    cr.draw_cube(q, [6, 4])
    cr.draw_cube(r, [1])
    cr.draw_link(q, r)
    cr.draw_link(p, q)
    cr.show_page()


if __name__ == "__main__":
    visualise([], [], "visualisation.pdf")
