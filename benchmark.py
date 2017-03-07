import argparse
from timeit import timeit
from collections import deque
import math

from graph import random_graph, Graph
from displaygraph import DisplayGraph

try:
    from displaygraph import config
except ImportError:
    print("Couldn't find fdag... skipping C-extension benchmarks.")
    fdag_imported = False
else:
    fdag_imported = True


class BenchmarkDisplayGraph(DisplayGraph):
    """Subclass of DisplayGraph for benchmarking. Doesn't create a window
    to display output and copies the graph it is initialized with, but
    otherwise is identical."""

    def __init__(self, graph, threaded=False, num_threads=4, update_algo=None):

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

        self.threaded = threaded
        self.num_threads = num_threads

        # Selected update method
        if update_algo == 'c_update' and fdag_imported is True:
            self.update = self.c_update
            config(self.c1, self.c2, self.c3, self.c4, self.threaded, self.num_threads)
        else:
            self.update = self.python_update

    def run_benchmark(self):
        for x in range(DisplayGraph.M):
            self.update()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Benchmarks!")

    parser.add_argument("-np", "--no-python", action="store_true",
                        help="Don't run python benchmark")
    parser.add_argument("-v", "--vertices", type=int, help="Number of vertices in graph")
    parser.add_argument("-e", "--edges", type=int, help="Number of edges in graph")

    args = parser.parse_args()

    graph_args = {}

    if args.vertices:
        graph_args['V'] = args.vertices
    if args.edges:
        graph_args['E'] = args.edges

    print("Starting benchmarks. This will take a minute...")

    graph = random_graph(**graph_args)

    if args.no_python is False:
        p_results = timeit('bmg.run_benchmark()', setup="from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, update_algo='python_update')", number=10)

        print("Python results: {}".format(p_results))

    if fdag_imported:

        # Single Threaded
        c_results = timeit('bmg.run_benchmark()', setup="from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, threaded=False, update_algo='c_update')", number=10)

        print("C results(single thread): {}".format(c_results))

        # Threaded
        num_threads = 1
        setup_str = "from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, threaded=True, num_threads={}, update_algo='c_update')"

        for x in range(5):
            num_threads = num_threads * 2

            c_results = timeit('bmg.run_benchmark()', setup=setup_str.format(num_threads), number=10)

            print("C results(multi-threaded ({0} threads): {1}".format(num_threads, c_results))
