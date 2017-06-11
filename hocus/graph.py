from enum import IntEnum


class Direction(IntEnum):
    UP = 0
    UPRIGHT = 1
    DOWNRIGHT = 2
    DOWN = 3
    DOWNLEFT = 4
    UPLEFT = 5

    def opposite(self):
        return Direction((self + 3) % 6)


# Face enum compatible with Direction
class Face(IntEnum):
    TOP = 0
    BACK = 1
    RIGHT = 2
    BOTTOM = 3
    FRONT = 4
    LEFT = 5

    def opposite(self):
        return Face((self + 3) % 6)

    def adjacents(self):
        return [Face((self + i) % 6) for i in [1, 2, 4, 5]]


class Node:
    def __init__(self, x, y, directions, neighbors=None):
        self.location = [x, y]
        self.directions = directions
        if neighbors is None:
            self.neighbors = [None] * 6
        else:
            self.neighbors = neighbors


class Graph:
    def __init__(self, nodes=None):
        if nodes is None:
            self.nodes = []
        else:
            self.nodes = nodes

    def test(self):
        for node in self.nodes:
            for i in range(6):
                if node.neighbors[i] and (node.neighbors[i].neighbors[(i + 3) % 6] != node):
                    print('Wrong link between nodes', node.location, 'and', node.neighbors[i].location)
