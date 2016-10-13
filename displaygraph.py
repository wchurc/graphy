import time
import turtle
import math
from graph import Graph


class Edge(object):
    
    def __init__(self, v, w):
        self.v = v
        self.w = w


class Vertex(object):
    
    def __init__(self, x, y):
        self.x = x
        self.y = y


class DisplayGraph(object):

    c1 = 10
    c2 = 50
    c3 = 100
    c4 = 10 
    M = 100
    
    def __init__(self, graph, window=None):

        if not isinstance(graph, Graph):
            raise Exception("DisplayGraph must be initialized with a Graph")

        self.graph = graph
        self.size = int(math.sqrt(len(graph.vertices)))
        self.scale = 50 

        self.window = window or turtle.Screen()
        self.window.tracer(0, 0)
        self.t = turtle.Turtle(visible=False)
        self.t.speed(0)

        self.vertices = []
        self.edges = []
        self.populate()
        self.active = True

    def populate(self):
        x, y = 0, 0
        for v in self.graph.vertices:
            self.vertices.append(Vertex(x * self.scale,  y * self.scale))
            x += 1
            if x >= self.size:
                x = 0
                y += 1

        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(Edge(self.vertices[i], self.vertices[w]))

    def update(self):
        
        for v in self.vertices:
            for w in self.vertices:
                if w is not v:
                    d = self.distance(v.x, v.y, w.x, w.y)
                    f = self.repulsion(d) * DisplayGraph.c4
                    x, y = [f*x for x in self.unit_to(w.x, w.y, v.x, v.y)]
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
        for v in self.vertices:
            self.draw_vertex(v)

        for e in self.edges:
            self.draw_edge(e)
        
        self.window.update()

    def display(self):

        for x in range(DisplayGraph.M):
            self.update()
            self.t.clear()
            self.draw()
        
        self.window.exitonclick()

    
    def draw_vertex(self, v):
        
        self.t.up()
        self.t.setpos(v.x,  
                      v.y)
        self.t.down()
        self.t.dot(10)
        

    def draw_edge(self, e):
        self.t.up()
        self.t.setpos(e.v.x,
                      e.v.y)
        self.t.down()
        self.t.setpos(e.w.x,
                      e.w.y)
    
    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        return cls.c3/d**2

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


