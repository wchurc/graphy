from graphy.displaygraph import DisplayGraph
from graphy.graph import random_graph
from graphy.components import Dragger


if __name__ == '__main__':
    g = random_graph(connected=True)
    d = DisplayGraph(g, update_algo='c_update')
    d.components.append(Dragger(d))

    d.display()
