import argparse
from timeit import timeit
from collections import deque, defaultdict
import math

from matplotlib import pyplot as plt

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


def time_it(update_algo, threaded=False, num_threads=0, number=10):
    setup_str = "from __main__ import graph, BenchmarkDisplayGraph; bmg = BenchmarkDisplayGraph(graph, update_algo='{update_algo}', threaded={threaded}, num_threads={num_threads})"
    return timeit('bmg.run_benchmark()',
                  setup=setup_str.format(update_algo=update_algo, num_threads=num_threads, threaded=threaded),
                  number=number)


def benchmark(graph, number=10):
    print("Starting benchmarks. This will take a minute...")

    results = []

    if args.no_python is False:
        p_results = time_it('python_update', number=number)
        results.append(('python', p_results))

        print("Python results: {}".format(p_results))

    if fdag_imported:

        # Single Threaded
        c_results = time_it('c_update', number=number, threaded=False)
        results.append(('C 01 thread', c_results))

        print("C results(single thread): {}".format(c_results))

        # Threaded
        num_threads = 1

        for x in range(5):
            num_threads = num_threads * 2

            c_results = time_it('c_update', number=number, num_threads=num_threads, threaded=True)
            results.append(('C {0:02d} threads'.format(num_threads), c_results))

            print("C results(multi-threaded ({0} threads): {1}".format(num_threads, c_results))

    return results


def parse_args():
    parser = argparse.ArgumentParser(description="Benchmarks!")

    parser.add_argument("-np", "--no-python", action="store_true",
                        help="Don't run python benchmark")
    parser.add_argument("-v", "--vertices", type=int, help="Number of vertices in graph")
    parser.add_argument("-e", "--edges", type=int, help="Number of edges in graph")
    parser.add_argument("-pl", "--plot", action="store_true", help="Plot results")
    parser.add_argument("-s", "--series", action="store_true", help="Run a series of benchmarks on different sized graphs")
    parser.add_argument("-n", "--number", type=int, help="Number of times to run benchmark (passed to timeit.timeit)")

    args = parser.parse_args()

    graph_args = {}

    if args.vertices:
        graph_args['V'] = args.vertices
    if args.edges:
        graph_args['E'] = args.edges

    return (args, graph_args)


def plot_results(x_axis, results):
    plt.ylabel('time')
    plt.xlabel('# of vertices')

    for key, value in sorted(results.items()):
        plt.plot(x_axis, value, label=key)

    plt.legend()
    plt.show()


if __name__ == '__main__':

    args, graph_args = parse_args()

    results = defaultdict(list)

    number = args.number if args.number else 10

    if args.series:
        x_axis = []
        for x in range(1, 9):
            V = x * 50
            x_axis.append(V)

            graph_args['V'] = V

            graph = random_graph(**graph_args)
            for algo, time in benchmark(graph, number=number):
                results[algo].append(time)

        if args.plot:
            plot_results(x_axis, results)

    else:
        graph = random_graph(**graph_args)
        for algo, time in benchmark(graph, number=number):
            results[algo].append(time)
