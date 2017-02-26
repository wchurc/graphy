import time
import turtle
import math
from graph import Graph, Edge, Vertex


class DisplayEdge(Edge):

    def __init__(self, v, w):
        super(DisplayEdge, self).__init__(v, w)
        self.color = 'gray'

    def draw(self, t):
        t.color(self.color)
        t.up()
        t.setpos(self.v.x, self.v.y)
        t.down()
        t.setpos(self.w.x, self.w.y)


class DisplayVertex(Vertex):

    def __init__(self, x, y):
        super(DisplayVertex, self).__init__(x, y)
        self.color = 'black'

    def draw(self, t):
        t.color(self.color)
        t.up()
        t.setpos(self.x, self.y)
        t.down()
        t.dot(5)


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
        for v in self.graph.vertices:
            self.vertices.append(DisplayVertex((x * self.xscale) + self.xoffset,
                                        (y * self.yscale) + self.yoffset))
            x += 1
            if x >= self.size:
                x = 0
                y += 1

        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(DisplayEdge(self.vertices[i], self.vertices[w]))

    def update(self):
        for v in self.vertices:
            for w in self.vertices:
                if w is not v:
                    d = self.distance(v.x, v.y, w.x, w.y)
                    f = self.repulsion(d) * DisplayGraph.c4
                    x, y = [f*x for x in self.unit_to(w.x, w.y, v.x, v.y)]
                    delta = math.sqrt(x**2 + y**2)
                    v.x += x
                    v.y += y

        for e in self.edges:
            d = self.distance(e.v.x, e.v.y, e.w.x, e.w.y)
            f = self.attraction(d) * DisplayGraph.c4
            x, y = [f*x for x in self.unit_to(e.v.x, e.v.y, e.w.x, e.w.y)]
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

        self.window.exitonclick()

    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        denom = d if d > cls.c2 else cls.c2
        return cls.c3/denom**2

    @staticmethod
    def distance(x1, y1, x2, y2):
        return math.sqrt((x1-x2)**2 + (y1-y2)**2)

    @staticmethod
    def unit_to(x1, y1, x2, y2):
        """ Returns the unit vector from x1,y1 to x2,y2"""
        x3 = x2 - x1
        y3 = y2 - y1
        mag = math.sqrt(x3**2 + y3**2)
        return (x3/mag, y3/mag)


