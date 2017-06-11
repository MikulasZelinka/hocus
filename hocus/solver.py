from hocus.graph import Direction, Face
from collections import deque, namedtuple


PathPart = namedtuple('PathPart', ['node_from', 'node_to', 'dir', 'face'])


def solve(graph):
    """
    Explores all reachable parts of graph from all starting points
    Args:
        graph: hocus.graph

    Returns:

    """

    explored = []

    def opposite_path_part(ppart):
        return PathPart(ppart.node_to, ppart.node_from, ppart.dir.opposite(), ppart.face)

    def mark_explored(ppart):
        explored.append(ppart)
        explored.append(opposite_path_part(ppart))

    def is_explored(ppart):
        return ppart in explored

    # find nodes with degree 0
    starts = [node for node in graph.nodes if len(node.directions) == 1]
    start = starts[0]
    start_dir = start.directions[0]
    q = deque()
    for face in Face(start_dir).adjacents():
        path_part = PathPart(start, start.neighbors[start_dir], start_dir, face)
        q.append(path_part)
        mark_explored(path_part)

    iter = 0
    while len(q) > 0:
        node_from, node_to, direction, face = q.popleft()
        candidates = []
        # print("Directions are {}".format(node_to.directions, Direction(face)))

        if Direction(face) in node_to.directions:
            candidates.append(PathPart(node_to, node_to.neighbors[face], face, direction.opposite()))
        else:
            for new_dir in face.adjacents():
                if Direction(new_dir) in node_to.directions:
                    # print("Appending {} {} {} {}".format(
                    #     node_to.location,
                    #     [Direction(i) for [i, _] in enumerate(node_to.neighbors) if _ is not None],
                    #     new_dir,
                    #     face
                    # ))
                    candidates.append(PathPart(node_to, node_to.neighbors[new_dir], new_dir, face))

        for path_part in candidates:
            if not is_explored(path_part):
                # print("Exploring from {} to {} in {} on {}".format(
                #     path_part.node_from.location,
                #     path_part.node_to.location,
                #     str(Direction(path_part.dir)),
                #     str(Face(path_part.face))
                # ))
                mark_explored(path_part)
                q.append(path_part)

        if ++iter % 100 == 0:
            print("Explored {} parts".format(len(explored)))


    # print(len(explored))

