"""
A python implementation of http://algs4.cs.princeton.edu/41graph/
"""
from random import randrange


class Graph(object):
    
    def __init__(self, V=0):
        self.vertices = [set() for x in range(V)]
        self.edges = 0

    def __repr__(self):
        return '\n'.join([str(v) for v in self.vertices])
    
    def add_edge(self, v, w):
        """ Add edge v-w to the graph"""
        if v not in self.vertices[w] and w not in self.vertices[v]:
            self.vertices[w].add(v)
            self.vertices[v].add(w)

    def adj(self, v):
        """ Yield vertices adjacent to v"""
        if v < len(self.vertices):
            for adjacent in self.vertices[v]:
                yield adjacent


def random_graph(V=50, E=50):
    graph = Graph(V)
    for i in range(E):
        graph.add_edge(randrange(0, V), randrange(0, V))
    return graph

