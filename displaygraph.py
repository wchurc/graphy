import turtle
import math
from graph import Graph


class Edge(object):
    pass


class Vertex(object):
    pass


class DisplayGraph(object):
    
    def __init__(self, graph, window=None):
        if not isinstance(graph, Graph):
            raise Exception("DisplayGraph must be initialized with a Graph")
        self.graph = graph
        self.size = int(math.sqrt(len(graph.vertices)))
        self.window = window

    def display(self):
        self.window == self.window or turtle.Screen()
        x, y = 0, 0
        for i in range(len(self.graph.vertices)):
            self.draw_vertex(x * 50, y * 50)
            x += 1
            if x >= self.size:
                x = 0
                y += 1

    
    def draw_vertex(self, x, y):
        t = turtle.Turtle()
        t.speed(0)
        t.up()
        t.setpos(x, y)
        t.down()
        t.circle(3)
        del t

    def draw_edge():
        pass


