from graphy.displaygraph import DragGraph
from graphy.graph import random_graph


if __name__ == '__main__':
    g = random_graph(connected=True)
    d = DragGraph(g, update_algo='c_update')

    d.display()

