from random import randrange
from queue import Queue

class Graph(object):
    
    def __init__(self, V=50):
        self.vertices = [set() for x in range(V)]
        self.edges = 0
        self._cc = []
        
    def __repr__(self):
        return '\n'.join([str(v) for v in self.vertices])
    
    def add_edge(self, v, w):
        """ Add edge v-w to the graph"""
        if v not in self.vertices[w] and w not in self.vertices[v] and v is not w:
            self.vertices[w].add(v)
            self.vertices[v].add(w)

    def connected_component(self, v):
        """ Returns the set of vertices reachable by v"""
        marked = set()
        q = Queue()
        q.put(v)
        while not q.empty():
            v = q.get()
            for w in self.vertices[v]:
                if w not in marked:
                    marked.add(w)
                    q.put(w)
        return marked


def random_graph(V=50, E=50):
    graph = Graph(V)
    for i in range(E):
        graph.add_edge(randrange(0, V), randrange(0, V))
    return graph

