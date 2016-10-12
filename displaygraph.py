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
            self.vertices.append(Vertex(x, y))
            x += 1
            if x >= self.size:
                x = 0
                y += 1

        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(Edge(self.vertices[i], self.vertices[w]))

    def update(self):
        pass

    def draw(self):
        for v in self.vertices:
            self.draw_vertex(v)

        for e in self.edges:
            self.draw_edge(e)
        
        self.window.update()

    def display(self):

        while self.active:
            self.active = False
            self.update()
            self.draw()
        
        self.window.exitonclick()

    
    def draw_vertex(self, v):
        
        self.t.up()
        self.t.setpos(v.x * self.scale,  
                      v.y * self.scale)
        self.t.down()
        self.t.dot(10)
        

    def draw_edge(self, e):
        self.t.up()
        self.t.setpos(e.v.x * self.scale,
                      e.v.y * self.scale)
        self.t.down()
        self.t.setpos(e.w.x * self.scale,
                      e.w.y * self.scale)


