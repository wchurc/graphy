from random import randrange, choice
from queue import Queue


class Edge(object):

    def __init__(self, v, w):
        self.v = v
        self.w = w


class Vertex(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Graph(object):

    def __init__(self, V=50):
        self.vertices = [set() for x in range(V)]
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


def random_graph(V=50, E=50, connected=False):
    graph = Graph(V)
    for i in range(E):
        graph.add_edge(randrange(0, V), randrange(0, V))
    if not connected:
        return graph
    component = max([graph.connected_component(x) for x in range(len(graph.vertices))])
    if len(component) < len(graph.vertices):
        disconnected = [x for x in range(len(graph.vertices)) if x not in component]
        for v in disconnected:
            graph.add_edge(v, choice(list(component)))
    return graph



