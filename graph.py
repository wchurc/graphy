from collections import namedtuple
from random import randrange, choice
from queue import Queue, PriorityQueue
import math


class Edge(object):

    def __init__(self, v, w):
        self.v = v
        self.w = w


class Vertex(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._neighbors = set()
        self.marked = False

    def __contains__(self, v_index):
        return v_index in self._neighbors

    def __iter__(self):
        return iter(self._neighbors)

    def __repr__(self):
        return "x: {0}, y: {1}\nneighbors: {2}".format(self.x, self.y,
                                                       self._neighbors.__repr__())
    def add(self, v_index):
        self._neighbors.add(v_index)

    def distance_to(self, w):
        """ Returns the from self to Vertex w"""
        return math.sqrt((self.x - w.x)**2 + (self.y - w.y)**2)

    def unit_to(self, w):
        """ Returns the unit vector from self to Vertex w"""
        x3 = w.x - self.x
        y3 = w.y - self.y
        mag = math.sqrt(x3**2 + y3**2)
        return (x3/mag, y3/mag)

    def cost_to(self, w):
        result = self.distance_to(w)

        return self.distance_to(w)



class Graph(object):

    def __init__(self, V=50):
        self.vertices = [Vertex(None, None) for x in range(V)]

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

    def dijkstra(self, start, finish):
        """ Returns the shortest path from start to finish as a list of indices.
        Also sets marked = True on every vertex it looks at."""

        def build_path():
            path = []
            node = finish
            while node != start:
                path.append(node)
                node = seen.get(node).prev

            path.append(start)
            return reversed(path)

        Data = namedtuple('Data', ['cost', 'prev'])

        seen = {start : Data(0, start)}
        done = set()

        pq = PriorityQueue()
        pq.put((0, start))

        while not pq.empty():
            cost, v = pq.get()

            self.vertices[v].marked = True

            # Check if finished
            if v == finish:
                return build_path()

            # There may be duplicates in the pq so check if v has been done already
            if v in done:
                continue

            # Check every neighbor of v
            for w in self.vertices[v]:
                assert w is not None
                if w not in done:

                    self.vertices[w].marked = True

                    w_cost = seen.get(v).cost + self.vertices[v].cost_to(self.vertices[w])

                    if w not in seen or seen.get(w).cost > w_cost:
                        # Add to pq and update seen
                        seen[w] = Data(w_cost, v)
                        pq.put((w_cost, w))

            done.add(v)


    def a_star(self, start, finish):
        """ Literally identical to the dijkstra implementation except this adds
        the distance to the finishing node when w_cost is calculated."""

        def build_path():
            path = []
            node = finish
            while node != start:
                path.append(node)
                node = seen.get(node).prev

            path.append(start)
            return reversed(path)

        Data = namedtuple('Data', ['cost', 'prev'])

        seen = {start : Data(0, start)}
        done = set()

        pq = PriorityQueue()
        pq.put((0, start))

        while not pq.empty():
            cost, v = pq.get()

            self.vertices[v].marked = True

            # Check if finished
            if v == finish:
                return build_path()

            # There may be duplicates in the pq so check if v has been done already
            if v in done:
                continue

            # Check every neighbor of v
            for w in self.vertices[v]:
                assert w is not None
                if w not in done:

                    self.vertices[w].marked = True

                    w_cost = seen.get(v).cost + \
                             self.vertices[v].cost_to(self.vertices[w]) + \
                             self.vertices[w].cost_to(self.vertices[finish])

                    if w not in seen or seen.get(w).cost > w_cost:
                        # Add to pq and update seen
                        seen[w] = Data(w_cost, v)
                        pq.put((w_cost, w))

            done.add(v)


def random_graph(V=80, E=50, connected=False):
    """ Generates a random graph with V vertices and E edges"""
    graph = Graph(V)
    for _ in range(E):
        graph.add_edge(randrange(0, V), randrange(0, V))
    if not connected:
        return graph

    component = max([graph.connected_component(x) for x in range(len(graph.vertices))])
    while len(component) < len(graph.vertices):
        for x in range(len(graph.vertices)):
            if x not in component:
                graph.add_edge(x, choice(list(component)))
                break

        component = graph.connected_component(component.pop())

    return graph



