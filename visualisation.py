from math import pi, cos, sin, sqrt

import cairo

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
        return

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

        edges = set(e - 1 for e in edges)
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


def visualise(vertical, slanted, filename):
    """Make a pdf showing the mess.

    Args:
        vertical: [[bool]] -- see format_datovych_souboru.txt
        slanted: [[bool]] -- see format_datovych_souboru.txt
        filename: str -- output filename

    """
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    cr = HocusContext(surface)

    # Distance between centers of adjacent cubes -- diagonal of one field (see
    # format_datovych_souboru.txt). Measured with Monsters, Inc. ruler.
    dist = 6 * mm

    field_height = dist * sin(pi / 6)
    field_width = dist * cos(pi / 6)

    N = len(vertical)
    M = len(vertical[0])

    # here i is indexing cubes, not fields
    for i in range(N + 1):
        # j also, but the number of cubes columns is the same as the number of
        # vertical edges columns
        for j in range(M):

            if j % 2 != i % 2:
                # cubes are only in two corners of a field
                continue

            p = Point(100 + field_width * j, 100 + field_height * i)

            edges = []
            if i > 0 and vertical[i - 1][j]:
                edges.append(1)
                cr.draw_link(p, p + Point(0, -2 * field_height))
            if i < N and vertical[i][j]:
                edges.append(4)

            if i > 0:
                if j > 0 and slanted[i - 1][j - 1]:
                    edges.append(6)
                    cr.draw_link(p, p + Point(-field_width, -field_height))
                if j < M - 1 and slanted[i - 1][j]:
                    edges.append(2)
                    cr.draw_link(p, p + Point(+field_width, -field_height))
            if i < N:
                if j > 0 and slanted[i][j - 1]:
                    edges.append(5)
                if j < M - 1 and slanted[i][j]:
                    edges.append(3)

            if edges:
                cr.draw_cube(p, edges)

    cr.show_page()


def read_array(filename):
    """Read a file with rows of "0"s ans "1"s and convert them to bools."""
    with open(filename, "r") as fin:
        return [
            [bool(int(x)) for x in row]
            for row in fin.read().split("\n") if row
        ]


if __name__ == "__main__":

    vertical = read_array("svisle_cary.txt")
    slanted = read_array("sikme_cary.txt")

    visualise(vertical, slanted, "visualisation.pdf")
