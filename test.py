import sys
from graph import random_graph
from displaygraph import DisplayGraph


if __name__ == '__main__':
    
    V = 100
    E = 50
    if len(sys.argv) >= 3:
        V = int(sys.argv[1])
        E = int(sys.argv[2])

    g = random_graph(V=V, E=E)
    print(g)
    dg = DisplayGraph(g)

    dg.display()
