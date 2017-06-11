from hocus.representation import get_graph
# from solver import solve
from hocus.visualisation import visualise


def main():
    graph = get_graph()
    # paths = solve(graph)
    visualise(graph, show_positions=True)


if __name__ == "__main__":
    main()
