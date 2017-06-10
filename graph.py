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
