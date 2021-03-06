from graphy.graph import random_graph
from graphy.displaygraph import DisplayGraph
from graphy.components import Dragger, Pathfinder

import argparse


def parse_args():
    parser = argparse.ArgumentParser(description="Test DisplayGraph")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("-c", "--c-update", action="store_true")
    group.add_argument("-p", "--python-update", action="store_true")

    parser.add_argument("-v", "--vertices", type=int, help="Number of vertices in graph")
    parser.add_argument("-e", "--edges", type=int, help="Number of edges in graph")
    parser.add_argument("-nc", "--not-connected", action="store_true", help="Don't automatically connect all components")
    parser.add_argument("-nt", "--num-threads", type=int, help="Number of threads to use during layout if using C-extension")

    return parser.parse_args()


def get_settings(args):
    graph_args = {}

    if args.vertices:
        graph_args['V'] = args.vertices
    if args.edges:
        graph_args['E'] = args.edges
    if args.not_connected:
        graph_args['connected'] = False
    else:
        graph_args['connected'] = True

    dgraph_args = {}

    if args.python_update:
        dgraph_args['update_algo'] = 'python_update'
    else:
        dgraph_args['update_algo'] = 'c_update'
        if args.num_threads:
            dgraph_args['num_threads'] = args.num_threads

    return graph_args, dgraph_args


if __name__ == '__main__':

    args = parse_args()

    graph_args, dgraph_args = get_settings(args)

    g = random_graph(**graph_args)

    dg = DisplayGraph(g, **dgraph_args)
    pf = Pathfinder(dg)
    dr = Dragger(dg)
    dg.components.append(pf)
    dg.components.append(dr)

    # Interface setup
    btn_x = -dg.width//2 + 20
    btn_y = dg.height//2 - 34
    dg.view.add_button(dg.view.Button(btn_x, btn_y - 60, "a_star", pf.draw_a_star))
    dg.view.add_button(dg.view.Button(btn_x, btn_y - 30, "dijkstra", pf.draw_dijkstra))
    dg.view.add_button(dg.view.Button(btn_x, btn_y, "new graph", dg.new_graph))

    dg.display()
