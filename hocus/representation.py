from hocus.graph import Node, Graph, Direction


def get_graph():
    vertical = read_array("data/svisle_cary.txt")
    slanted = read_array("data/sikme_cary.txt")

    N = len(vertical)
    M = len(vertical[0])

    node_array = [
        [Node(0, 0, []) if i % 4 == j % 4 else None for j in range(2 * M)]
        for i in range(2 * (N + 1))
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
                neighbors[Direction.UP] = node_array[(i - 2) * 2][j * 2]
            if i < N and vertical[i][j]:
                directions.append(Direction.DOWN)
                neighbors[Direction.DOWN] = node_array[(i + 2) * 2][j * 2]

            if i > 0:
                if j > 0 and slanted[i - 1][j - 1]:
                    directions.append(Direction.UPLEFT)
                    neighbors[Direction.UPLEFT] = node_array[(i - 1) * 2][(j - 1) * 2]
                if j < M - 1 and slanted[i - 1][j]:
                    directions.append(Direction.UPRIGHT)
                    neighbors[Direction.UPRIGHT] = node_array[(i - 1) * 2][(j + 1) * 2]
            if i < N:
                if j > 0 and slanted[i][j - 1]:
                    directions.append(Direction.DOWNLEFT)
                    neighbors[Direction.DOWNLEFT] = node_array[(i + 1) * 2][(j - 1) * 2]
                if j < M - 1 and slanted[i][j]:
                    directions.append(Direction.DOWNRIGHT)
                    neighbors[Direction.DOWNRIGHT] = node_array[(i + 1) * 2][(j + 1) * 2]

            node_array[i * 2][j * 2].location = [j * 2, i * 2]
            node_array[i * 2][j * 2].directions = directions
            node_array[i * 2][j * 2].neighbors = neighbors

    node_array = add_special_nodes(node_array)

    nodes = [
        node for row in node_array for node in row
        if node and node.directions
    ]

    return Graph(nodes)


def add_special_nodes(node_array):

    # TOP-RIGHT corner:
    # Middle node (at 108, 14)
    middle_x = 108
    middle_y = 14
    middle_node = Node(middle_x, middle_y, [Direction.UP, Direction.DOWNRIGHT, Direction.DOWN, Direction.DOWNLEFT])
    node_array[middle_y][middle_x] = middle_node

    middle_node.neighbors[Direction.UP] = node_array[middle_y - 2][middle_x]
    node_array[middle_y - 2][middle_x].neighbors[Direction.DOWN] = middle_node

    middle_node.neighbors[Direction.DOWN] = node_array[middle_y + 2][middle_x]
    node_array[middle_y + 2][middle_x].neighbors[Direction.UP] = middle_node

    # Down-right node
    down_right_x = middle_x + 4
    down_right_y = middle_y + 4
    down_right_node = Node(down_right_x, down_right_y, [Direction.UPLEFT])
    node_array[down_right_y][down_right_x] = down_right_node

    down_right_node.neighbors[Direction.UPLEFT] = middle_node
    middle_node.neighbors[Direction.DOWNRIGHT] = down_right_node

    # Down-left node
    down_left_x = middle_x - 3
    down_left_y = middle_y + 3
    down_left_node = Node(down_left_x, down_left_y, [Direction.UPRIGHT, Direction.DOWNRIGHT])
    node_array[down_left_y][down_left_x] = down_left_node

    down_left_node.neighbors[Direction.UPRIGHT] = middle_node
    middle_node.neighbors[Direction.DOWNLEFT] = down_left_node

    down_left_node.neighbors[Direction.DOWNRIGHT] = node_array[down_left_y + 3][down_left_x + 3]
    node_array[down_left_y + 3][down_left_x + 3].directions.append(Direction.UPLEFT)
    node_array[down_left_y + 3][down_left_x + 3].neighbors[Direction.UPLEFT] = down_left_node

    # LEFT-MIDDLE part:

    return node_array


def read_array(filename):
    """Read a file with rows of "0"s and "1"s and convert them to bools."""
    with open(filename, "r") as fin:
        return [
            [bool(int(x)) for x in row]
            for row in fin.read().split("\n") if row
        ]
