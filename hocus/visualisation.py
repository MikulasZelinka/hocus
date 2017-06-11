from math import pi, cos, sin, sqrt

import cairocffi as cairo

# A4
# HEIGHT, WIDTH = 8.3 * 72, 11.7 * 72

# A3
HEIGHT, WIDTH = 11.7 * 72, 2 * 8.3 * 72

mm = 72 / 25.4  # dpi / (number of millimeters in one inch)


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

    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2)

    def dist(self, q):
        return (self - q).norm()


class HocusContext(cairo.Context):

    # distance between two edges of a connecting link in the 2D projection
    # measured with Monsters, Inc. ruler.
    width = mm

    # distance from the middle of a cube to one of its vertices in the 2D
    # projection
    edge = width / cos(pi / 6)

    def draw_point(self, p):
        """Draw cross at p"""
        length = 3
        self.set_line_width(0.1)
        self.set_source_rgba(0, 0, 1, 1)
        self.move_to(p.x + length, p.y)
        self.line_to(p.x - length, p.y)
        self.stroke()
        self.move_to(p.x, p.y + length)
        self.line_to(p.x, p.y - length)
        self.stroke()

    def draw_line(self, p, q, line_width=0.8, line_cap=cairo.LINE_CAP_ROUND):
        """Draw line between p and q"""
        self.set_line_width(line_width)
        self.set_line_cap(line_cap)
        self.move_to(*p)
        self.line_to(*q)
        self.stroke()

    def draw_cube(self, middle, edges, explain=False):
        """Draw a cube and some adjacent lines.

        (Lines which cannot be drawn without knowledge of edges.)

        Args:
            middle: Point -- center of the 2D projection of the cube
            edges: Iterable -- list of edges adjacent to the cube. Numbered
                from top clockwise 1..6.
            explain: bool -- Should different parts of the cube be drawn in
                different colours?
        """

        # edges = set(e - 2 for e in edges)
        top = middle - Point(0, self.edge)

        # No comment would help you. Draw it (with explain=True).
        if explain:
            self.set_source_rgb(1, 0, 0)
        for i in [0, 2, 4]:
            if i not in edges and (i + 2) % 6 not in edges:
                self.draw_line(
                    middle,
                    top.rotated((1 + i) * pi / 3, middle)
                )
            if i in edges:
                self.draw_line(middle, top.rotated(i * pi / 3, middle))

        if explain:
            self.set_source_rgb(0.6, 0.6, 0)
        for i in range(6):
            if not (i in edges or (i + 1) % 6 in edges):
                self.draw_line(
                    top.rotated(i * pi / 3, middle),
                    top.rotated((i + 1) * pi / 3, middle)
                )

        if explain:
            self.set_source_rgb(0.3, 0.3, 0.5)
        for i in range(6):
            if i in edges:
                vert = top.rotated(i * pi / 3, middle)

                for sgn in [-1, 1]:
                    if i % 2 == 0 or (i - sgn) % 6 not in edges:
                        q = middle.rotated(sgn * pi / 3, vert)
                        self.draw_line(q, q + vert - middle)
        if explain:
            self.set_source_rgb(0, 0, 0)

    def draw_link(self, a, b):
        """Draw connection between two cubes"""

        p = a + (b - a) * (self.edge / b.dist(a))
        q = b + (a - b) * (self.edge / b.dist(a))

        self.draw_line(p, q)

        # outer lines are shorter
        r = (p - q.rotated(pi / 3, p)) * (self.edge / p.dist(q))
        r2 = (p - r).rotated(-2 * pi / 3, p) - p
        self.draw_line(p - r, q - r2)
        self.draw_line(p + r2, q + r)


def visualise(graph, filename="data/visualisation.pdf", show_positions=True):
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    cr = HocusContext(surface)

    dist = 3 * mm

    field_height = dist * sin(pi / 6)
    field_width = dist * cos(pi / 6)

    def transform(p):
        return Point(p.x * field_width + 100, p.y * field_height + 100)

    for node in graph.nodes:
        p = transform(Point(*node.location))
        for n in node.neighbors:
            if n is not None:
                cr.draw_link(p, transform(Point(*n.location)))

        cr.draw_cube(p, node.directions)
        if show_positions:
            cr.move_to(*p)
            cr.set_source_rgb(1, 0, 0)
            cr.set_font_size(2)
            cr.show_text(str(node.location))
            cr.set_source_rgb(0, 0, 0)

    cr.show_page()
    print('Saved result to', filename)
