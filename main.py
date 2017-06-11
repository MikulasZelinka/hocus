from hocus.representation import get_graph
from hocus.solver import solve
from hocus.visualisation import visualise


def main():
    graph = get_graph()
    graph.test()
    paths = solve(graph)
    visualise(graph)


if __name__ == "__main__":
    main()
