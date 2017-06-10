from graph import Point, Node, Graph, Direction


def get_graph():
    vertical = read_array("svisle_cary.txt")
    slanted = read_array("sikme_cary.txt")

    N = len(vertical)
    M = len(vertical[0])

    nodeArray = [[Node(0, 0, []) for _ in range(M)] for _ in range(N + 1)]

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
                neighbors[Direction.UP] = nodeArray[i-1][j]
            if i < N and vertical[i][j]:
                directions.append(Direction.DOWN)
                neighbors[Direction.DOWN] = nodeArray[i+1][j]

            if i > 0:
                if j > 0 and slanted[i - 1][j - 1]:
                    directions.append(Direction.UPLEFT)
                    neighbors[Direction.UPLEFT] = nodeArray[i - 1][j - 1] if j % 2 == 0 else nodeArray[i][j - 1]
                if j < M - 1 and slanted[i - 1][j]:
                    directions.append(Direction.UPRIGHT)
                    neighbors[Direction.UPRIGHT] = nodeArray[i - 1][j + 1] if j % 2 == 0 else nodeArray[i][j + 1]
            if i < N:
                if j > 0 and slanted[i][j - 1]:
                    directions.append(Direction.DOWNLEFT)
                    neighbors[Direction.DOWNLEFT] = nodeArray[i][j - 1] if j % 2 == 0 else nodeArray[i + 1][j - 1]
                if j < M - 1 and slanted[i][j]:
                    directions.append(Direction.DOWNRIGHT)
                    neighbors[Direction.DOWNRIGHT] = nodeArray[i][j + 1] if j % 2 == 0 else nodeArray[i + 1][j + 1]

            nodeArray[i][j].location = Point(j, i)
            nodeArray[i][j].directions = directions
            nodeArray[i][j].neighbors = neighbors

    nodes = [node for row in nodeArray for node in row]
    nodes = list(filter(lambda node: len(node.directions) > 0, nodes))

    return Graph(nodes)



def read_array(filename):
    """Read a file with rows of "0"s and "1"s and convert them to bools."""
    with open(filename, "r") as fin:
        return [
            [bool(int(x)) for x in row]
            for row in fin.read().split("\n") if row
        ]


