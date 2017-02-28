import time
import turtle
import math
from graph import Graph, Edge, Vertex


class DisplayEdge(object):

    def __init__(self, v, w):

        assert isinstance(v, DisplayVertex) and isinstance(w, DisplayVertex)

        self.v = v
        self.w = w
        self.color = 'gray'
        self.size = 2

    def draw(self, t):
        t.color(self.color)
        t.pensize(self.size)
        t.up()
        t.setpos(self.v.x, self.v.y)
        t.down()
        t.setpos(self.w.x, self.w.y)


class DisplayVertex(object):

    def __init__(self, vertex):

        assert isinstance(vertex, Vertex)

        self.v = vertex
        self.size = 5
        self._color = 'blue'
        self._marked_color = 'yellow'
        self._highlighted_color = 'red'
        self.highlighted = False

    def draw(self, t):
        t.up()
        t.setpos(self.v.x + self.size, self.v.y)
        t.setheading(90)
        t.down()
        t.fillcolor(self.color)
        t.pencolor('black')
        t.begin_fill()
        t.circle(self.size)
        t.end_fill()
        #t.dot(self.size, self.color)


    @property
    def x(self):
        return self.v.x

    @x.setter
    def x(self, value):
        self.v.x = value

    @property
    def y(self):
        return self.v.y

    @y.setter
    def y(self, value):
        self.v.y = value

    @property
    def color(self):
        if self.highlighted:
            return self._highlighted_color
        if self.v.marked:
            return self._marked_color
        return self._color

    def distance_to(self, w):
        return self.v.distance_to(w)

    def unit_to(self, w):
        return self.v.unit_to(w)


class DisplayGraph(object):

    c1 = 10
    c2 = 50
    c3 = 100
    c4 = 10
    M = 300

    def __init__(self, graph, window=None):

        if not isinstance(graph, Graph):
            raise Exception("DisplayGraph must be initialized with a Graph")

        self.graph = graph
        self.size = int(math.sqrt(len(graph.vertices)))

        self.window = window or turtle.Screen()
        self.window.tracer(0, 0)
        self.t = turtle.Turtle(visible=False)
        self.t.speed(0)

        self.xscale = (self.window.window_width() // 2) // self.size
        self.yscale = (self.window.window_height() // 2) // self.size
        self.xoffset = -self.window.window_width() // 4
        self.yoffset = -self.window.window_height() // 4

        self.vertices = []
        self.edges = []
        self.populate()

    def populate(self):

        x, y = 0, 0

        # Create DisplayVertices
        for v in self.graph.vertices:
            v.x = (x * self.xscale) + self.xoffset
            v.y = (y * self.yscale) + self.yoffset
            self.vertices.append(DisplayVertex(v))

            x += 1
            if x >= self.size:
                x = 0
                y += 1

        # Create DisplayEdges
        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(DisplayEdge(self.vertices[i], self.vertices[w]))

    def update(self):
        for v in self.vertices:
            for w in self.vertices:
                if w is not v:
                    d = v.distance_to(w)
                    f = self.repulsion(d) * DisplayGraph.c4
                    x, y = [f*x for x in w.unit_to(v)]
                    delta = math.sqrt(x**2 + y**2)
                    v.x += x
                    v.y += y

        for e in self.edges:
            d = e.v.distance_to(e.w)
            f = self.attraction(d) * DisplayGraph.c4
            x, y = [f*x for x in e.v.unit_to(e.w)]
            e.v.x += x
            e.v.y += y
            e.w.x -= x
            e.w.y -= y


    def draw(self):

        for e in self.edges:
            e.draw(self.t)

        for v in self.vertices:
            v.draw(self.t)

        self.window.update()

    def display(self):

        for x in range(DisplayGraph.M):
            self.update()
            self.t.clear()
            self.draw()

        path = self.graph.dijkstra(0, len(self.graph.vertices) - 1)

        for v in path:
            self.vertices[v].highlighted = True

        self.t.clear()
        self.draw()

        self.window.exitonclick()

    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        denom = d if d > cls.c2 else cls.c2
        return cls.c3/denom**2
