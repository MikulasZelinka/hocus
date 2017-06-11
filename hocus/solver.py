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
    print("\nSolver started")

    explored = set()
    for node in graph.nodes:
        node.coloring = {d: [False] * 4 for d in node.directions}

    def dirface_to_int(direction, face):
        return 0

    def opposite_path_part(ppart):
        return PathPart(ppart.node_to, ppart.node_from, ppart.dir.opposite(), ppart.face)

    def mark_explored(ppart):
        ppart.node_from.coloring[ppart.dir][dirface_to_int(ppart.dir, ppart.face)] = True
        ppart.node_to.coloring[ppart.dir.opposite()][dirface_to_int(ppart.dir.opposite(), ppart.face)] = True

        explored.add(ppart)
        explored.add(opposite_path_part(ppart))

    def is_explored(ppart):
        # could do this in fast constant time by checking the node coloring
        # no need for speed, favoring readability
        return ppart in explored

    # find nodes with degree 0
    starts = [node for node in graph.nodes if len(node.directions) == 1]
    for start in starts:
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

        iter += 1
        if iter % 1000 == 0:
            print("Explored {} parts".format(len(explored)))

    total_explored = len(explored) // 2
    total_possible = sum([len(node.directions) for node in graph.nodes]) * 4 // 2

    print("Explored in total: {}".format(total_explored))
    print("All edgefaces: {}".format(total_possible))
    print("Left uncolored: {} ({:.2f})%".format(
        total_possible - total_explored,
        100 * (total_possible - total_explored) / total_possible
    ))
    print("Solver finished\n")



