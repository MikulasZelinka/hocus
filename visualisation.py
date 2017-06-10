from math import pi, cos, sin, sqrt
from graph import Direction, Point

import cairocffi as cairo

# A4
# HEIGHT, WIDTH = 8.3 * 72, 11.7 * 72

# A3
HEIGHT, WIDTH = 11.7 * 72, 2 * 8.3 * 72

mm = 72 / 25.4  # dpi / (number of millimeters in one inch)

class HocusContext(cairo.Context):

    # distance between two edges of a connecting link in the 2D projection
    # measured with Monsters, Inc. ruler.
    width = mm

    # distance from the middle of a cube to one of its vertices in the 2D
    # projection
    edge = width / cos(pi / 6)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.later_lines = []

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
                  procrastinate=True):
        """Draw line between p and q... later (if procrastinate=True)"""
        if not procrastinate:
            self.set_line_width(line_width)
            self.set_line_cap(line_cap)
            self.move_to(*p)
            self.line_to(*q)
            self.stroke()
        else:
            self.later_lines.append((p, q, line_width, line_cap))

    def stop_procrastinating(self):
        """Draw all postponed lines"""
        for args in self.later_lines:
            self.draw_line(*args, procrastinate=False)
        self.later_lines = []

    def fill_path(self, path, color=(0.2, 0.1, 0.9)):
        self.move_to(*path[0])
        for p in path[1:]:
            self.line_to(*p)
        self.close_path()
        self.set_source_rgb(*color)
        self.fill()
        self.set_source_rgb(0, 0, 0)

    def draw_cube(self, middle, edges, coloring=None, explain=False):
        """Draw a cube and some adjacent lines.

        (Lines which cannot be drawn without knowledge of edges.)

        Args:
            middle: Point -- center of the 2D projection of the cube
            edges: Iterable -- list of edges adjacent to the cube. Numbered
                from top clockwise 1..6.
            coloring: [(bool, bool)] -- TODO
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
                p = top.rotated(i * pi / 3, middle)
                q = top.rotated((i + 1) * pi / 3, middle)
                if coloring and coloring[(i+1)%2][0] or coloring[(i + 2) % 6][1]:
                    self.fill_path([middle, p, q])
                self.draw_line(p, q)

        if explain:
            self.set_source_rgb(0.3, 0.3, 0.5)
        for i in range(6):
            if i in edges:
                vert = top.rotated(i * pi / 3, middle)

                for sgn in [-1, 1]:
                    if i % 2 == 0 or (i - sgn) % 6 not in edges:
                        if coloring and coloring[i][max(0, sgn)]:
                            q = middle.rotated(sgn * pi / 3, vert)
                            self.fill_path(
                                [middle, vert, q + vert - middle, q]
                            )
                        q = middle.rotated(sgn * pi / 3, vert)
                        self.draw_line(q, q + vert - middle)

        if explain:
            self.set_source_rgb(0, 0, 0)

    def draw_link(self, a, b, coloring=None):
        """Draw connection between two cubes"""

        p = a + (b - a) * (self.edge / b.dist(a))
        q = b + (a - b) * (self.edge / b.dist(a))

        # outer lines are shorter
        r = (p - q.rotated(pi / 3, p)) * (self.edge / p.dist(q))
        r2 = (p - r).rotated(-2 * pi / 3, p) - p

        if coloring:
            self.set_source_rgb(0.3, 0, 0.9)
            if coloring[0]:
                self.fill_path([p, q, q - r2, p - r, p])
            if coloring[1]:
                self.fill_path([p, q, q + r, p + r2, p])
            self.set_source_rgb(0, 0, 0)

        self.draw_line(p, q)

        self.draw_line(p - r, q - r2)
        self.draw_line(p + r2, q + r)


def visualise(graph, filename="visualisation.pdf"):
    surface = cairo.PDFSurface(filename, WIDTH, HEIGHT)
    cr = HocusContext(surface)

    dist = 6 * mm

    field_height = dist * sin(pi / 6)
    field_width = dist * cos(pi / 6)

    for node in graph.nodes:
        p = Point(node.location.x * field_width + 100, node.location.y * field_height + 100)
        if Direction.UP in node.directions:
            cr.draw_link(p, p + Point(0, -2 * field_height))
        if Direction.UPLEFT in node.directions:
            cr.draw_link(p, p + Point(-field_width, -field_height))
        if Direction.UPRIGHT in node.directions:
            cr.draw_link(p, p + Point(+field_width, -field_height))

        cr.draw_cube(p, node.directions)
    cr.show_page()
