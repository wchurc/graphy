from timeit import timeit
from collections import deque
import math

from graph import random_graph, Graph
from displaygraph import DisplayGraph, config


class BenchmarkDisplayGraph(DisplayGraph):
    """Subclass of DisplayGraph for benchmarking. Doesn't create a window
    to display output and copies the graph it is initialized with, but 
    otherwise is identical."""

    def __init__(self, graph, update_algo=None):

        if not isinstance(graph, Graph):
            raise Exception("DisplayGraph must be initialized with a Graph")

        self.graph = graph.copy()

        # Layout and display related setup
        self.size = int(math.sqrt(len(self.graph.vertices)))

        self.xscale = (1500 // 2) // self.size
        self.yscale = (1028 // 2) // self.size
        self.xoffset = -1500 // 4
        self.yoffset = -1028 // 4

        # Graph setup
        self.vertices = []
        self.edges = []
        self.populate()

        # Initialize queue for selected vertices
        self.selected_queue = deque(maxlen=2)

        # Pass constants to fdag
        config(self.c1, self.c2, self.c3, self.c4)

        # Selected update method
        if update_algo == 'c_update':
            self.update = self.c_update
        else:
            self.update = self.python_update

    def run_benchmark(self):
        for x in range(DisplayGraph.M):
            self.update()


if __name__ == '__main__':
    graph = random_graph()

    p_results = timeit('bmg.run_benchmark()', setup="from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, update_algo='python_update')", number=10)

    print("Python results: {}".format(p_results))

    c_results = timeit('bmg.run_benchmark()', setup="from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, update_algo='c_update')", number=10)

    print("C results: {}".format(c_results))

