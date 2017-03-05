import argparse
import random
from graph import random_graph
from displaygraph import DisplayGraph


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Test DisplayGraph")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--c-single-threaded", action="store_true")
    group.add_argument("-p", "--python", action="store_true")

    parser.add_argument("-v", "--vertices", type=int, help="Number of vertices in graph")
    parser.add_argument("-e", "--edges", type=int, help="Number of edges in graph")
    parser.add_argument("-nc", "--not-connected", action="store_true", help="Don't automatically connect all components")


    args = parser.parse_args()

    graph_args = {}
    if args.vertices:
        graph_args['V'] = args.vertices
    if args.edges:
        graph_args['E'] = args.edges
    if args.not_connected:
        graph_args['connected'] = False
    else:
        graph_args['connected'] = True


    g = random_graph(**graph_args)

    dgraph_args = {}
    if args.c_single_threaded:
        dgraph_args['update_algo'] = 'c_update'
    elif args.python:
        dgraph_args['update_algo'] = 'python_update'

    dg = DisplayGraph(g, **dgraph_args)

    dg.display()
