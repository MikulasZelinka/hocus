from hocus.graph import Node, Graph, Direction


def get_graph():
    vertical = read_array("data/svisle_cary.txt")
    slanted = read_array("data/sikme_cary.txt")

    N = len(vertical)
    M = len(vertical[0])

    node_array = [
        [Node(0, 0, []) if i % 2 == j % 2 else None for j in range(M)]
        for i in range(N + 1)
    ]

    for i in range(N + 1):
        # j also, but the number of cubes columns is the same as the number of
        # vertical edges columns
        for j in range(M):
            if j % 2 != i % 2:
                # cubes are only in two corners of a field
                continue

            directions = []
            neighbors = [None] * 6

            if i > 0 and vertical[i - 1][j]:
                directions.append(Direction.UP)
                neighbors[Direction.UP] = node_array[i-2][j]
            if i < N and vertical[i][j]:
                directions.append(Direction.DOWN)
                neighbors[Direction.DOWN] = node_array[i+2][j]

            if i > 0:
                if j > 0 and slanted[i - 1][j - 1]:
                    directions.append(Direction.UPLEFT)
                    neighbors[Direction.UPLEFT] = node_array[i-1][j - 1]
                if j < M - 1 and slanted[i - 1][j]:
                    directions.append(Direction.UPRIGHT)
                    neighbors[Direction.UPRIGHT] = node_array[i-1][j + 1]
            if i < N:
                if j > 0 and slanted[i][j - 1]:
                    directions.append(Direction.DOWNLEFT)
                    neighbors[Direction.DOWNLEFT] = node_array[i+1][j - 1]
                if j < M - 1 and slanted[i][j]:
                    directions.append(Direction.DOWNRIGHT)
                    neighbors[Direction.DOWNRIGHT] = node_array[i+1][j + 1]

            node_array[i][j].location = [j, i]
            node_array[i][j].directions = directions
            node_array[i][j].neighbors = neighbors

    nodes = [
        node for row in node_array for node in row
        if node and node.directions
    ]

    return Graph(nodes)


def read_array(filename):
    """Read a file with rows of "0"s and "1"s and convert them to bools."""
    with open(filename, "r") as fin:
        return [
            [bool(int(x)) for x in row]
            for row in fin.read().split("\n") if row
        ]
