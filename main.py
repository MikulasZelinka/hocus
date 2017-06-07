from representation import get_graph
from solver import solve
from visualisation import visualise


def main():
    graph = get_graph()
    paths = solve(graph)
    visualise(graph, paths)
    print('42')


if __name__ == "__main__":
    main()
