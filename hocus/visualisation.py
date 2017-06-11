from math import pi, cos, sin, sqrt

import cairocffi as cairo

from hocus.graph import Direction

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.postponed = {}
        self.rgb = (0, 0, 0)

    def set_source_rgb(self, r, g, b):
        self.rgb = (r, g, b)
        super().set_source_rgb(r, g, b)

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

    def draw_line(self,
                  p,
                  q,
                  line_width=0.8,
                  line_cap=cairo.LINE_CAP_ROUND,
                  procrastinate=1000):
        """Draw line between p and q... later"""
        if procrastinate == 0:
            self.set_line_width(line_width)
            self.set_line_cap(line_cap)
            self.move_to(*p)
            self.line_to(*q)
            self.stroke()
        else:
            rgb = self.rgb
            self.postponed.setdefault(procrastinate, [])
            self.postponed[procrastinate].append(
                (self.draw_line, (p, q, line_width, line_cap), rgb)
            )

    def fill_path(self, path, color=(0.2, 0.1, 0.9), procrastinate=0):
        if procrastinate == 0:
            self.move_to(*path[0])
            for p in path[1:]:
                self.line_to(*p)
            self.close_path()
            rgb = self.rgb
            self.set_source_rgb(*color)
            self.fill()
            self.set_source_rgb(*rgb)
        else:
            self.postponed.setdefault(procrastinate, [])
            self.postponed[procrastinate].append(
                (self.fill_path, (path, color), self.rgb)
            )

    def stop_procrastinating(self):
        """Draw all postponed objects

        A. k. a layers.
        """
        for layer, l in sorted(self.postponed.items()):
            for fun, args, rgb in l:
                self.set_source_rgb(*rgb)
                fun(*args, procrastinate=0)
        self.postponed = {}

    def draw_cube(self, middle, edges, coloring=None, explain=False):
        """Draw a cube and some adjacent lines.

        (Lines which cannot be drawn without knowledge of edges.)

        Args:
            middle: Point -- center of the 2D projection of the cube
            edges: Iterable -- list of edges adjacent to the cube. Numbered
                from top clockwise 1..6.
            coloring: [(bool, bool)] -- list of six pairs of bools indicating
                whether given half of each of the six incoming edges should be
                colored.
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

        for i in range(6):
            if not (i in edges or (i + 1) % 6 in edges):
                p = top.rotated(i * pi / 3, middle)
                q = top.rotated((i + 1) * pi / 3, middle)
                if explain:
                    self.set_source_rgb(0.6, 0.6, 0)
                self.draw_line(p, q)

        for i in range(6):
            if i in edges:
                vert = top.rotated(i * pi / 3, middle)

                for sgn in [-1, 1]:
                    if i % 2 == 0 or (i - sgn) % 6 not in edges:
                        q = middle.rotated(sgn * pi / 3, vert)
                        if explain:
                            self.set_source_rgb(0.3, 0.3, 0.5)
                        self.draw_line(q, q + vert - middle)

        if explain:
            self.set_source_rgb(0, 0, 0)

    def draw_link(self, a, b, coloring=None, fill_color=(0.3, 0, 0.9)):
        """Draw connection between two cubes"""

        p = a + (b - a) * (self.edge / b.dist(a))
        q = b + (a - b) * (self.edge / b.dist(a))

        # outer lines are shorter
        r = (p - q.rotated(pi / 3, p)) * (self.edge / p.dist(q))
        r2 = (p - r).rotated(-2 * pi / 3, p) - p

        self.draw_line(p, q)

        self.draw_line(p - r, q - r2)
        self.draw_line(p + r2, q + r)


def visualise(graph, filename="data/visualisation.pdf", show_positions=False):
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    cr = HocusContext(surface)

    dist = 3 * mm

    field_height = dist * sin(pi / 6)
    field_width = dist * cos(pi / 6)

    def transform(p):
        return Point(p.x * field_width + 100, p.y * field_height + 100)

    for node in graph.nodes:
        p = transform(Point(*node.location))
        for d, n in enumerate(node.neighbors):
            # draw only links going downish
            if d in [2, 3, 4] and n is not None:
                q = transform(Point(*n.location))
                cr.draw_link(p, q)

                coloring = node.coloring.get(d, [])[:2]
                if not coloring:
                    continue
                coloring = list(reversed(coloring))
                colors = [(0.8, 0.2, 1) if c else (1, 1, 1) for c in coloring]

                # point in the 2D projection of the current cube nearest to the
                # negihbouring cube
                nearest = p + (q - p) * (HocusContext.edge / p.dist(q))

                # (see a picture of a cube...)
                angle = 2 * pi / 3 if d == Direction.DOWN else pi / 3

                # left/right 2D projection vertices when looking in the
                # direction of the neighbour
                left = nearest.rotated(angle, p)
                right = nearest.rotated(-angle, p)
                p2 = Point(*p)
                q2 = Point(*q)

                # the slanted actually start earlier
                diff = nearest - p
                if d != Direction.DOWN:
                    left -= diff
                    right -= diff
                    p2 -= diff
                else:
                    q2 += diff

                # draw from top to bottom, vertical links first
                pl = 2 * node.location[1] + (1 if d != Direction.DOWN else 0)
                cr.fill_path(
                    [p2, left, q2 + left - p2, q2],
                    color=colors[1],
                    procrastinate=pl
                )
                cr.fill_path(
                    [p2, right, q2 + right - p2, q2],
                    color=colors[0],
                    procrastinate=pl
                )

        cr.draw_cube(p, node.directions)
    cr.stop_procrastinating()
    cr.show_page()
    print('Saved result to', filename)
