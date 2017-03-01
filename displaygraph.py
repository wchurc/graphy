import time
import turtle
import math
from graph import Graph, Edge, Vertex, random_graph
from collections import deque


class DisplayEdge(object):

    def __init__(self, v, w):

        assert isinstance(v, DisplayVertex) and isinstance(w, DisplayVertex)

        self.v = v
        self.w = w
        self.size = 2

    def draw(self, t):
        t.color(self.color)
        t.pensize(self.size)
        t.up()
        t.setpos(self.v.x, self.v.y)
        t.down()
        t.setpos(self.w.x, self.w.y)

    @property
    def color(self):
        if self.v.highlighted and self.w.highlighted:
            return 'red'
        return 'gray'


class DisplayVertex(object):

    def __init__(self, vertex):

        assert isinstance(vertex, Vertex)

        self.v = vertex
        self.size = 7
        self._color = 'blue'
        self._marked_color = 'yellow'
        self._highlighted_color = 'red'
        self.highlighted = False
        self.selected = False

    def draw(self, t):
        t.up()
        t.setpos(self.v.x + self.size, self.v.y)
        t.setheading(90)
        t.down()
        t.fillcolor(self.color)
        t.pensize(2)
        if self.selected:
            t.pencolor('orange')
        else:
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
    M = 150

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

        self.selected_queue = deque(maxlen=2)

        self.buttons = []
        self.buttons.append(Button(-500, 300, "a_star", self.draw_a_star))
        self.buttons.append(Button(-500, 330, "dijkstra", self.draw_dijkstra))
        self.buttons.append(Button(-500, 360, "new graph", self.new_graph))

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


    def draw(self, buttons=True):

        if buttons:
            for b in self.buttons:
                b.draw(self.t)

        for e in self.edges:
            e.draw(self.t)

        for v in self.vertices:
            v.draw(self.t)

        self.window.update()

    def display(self):

        for x in range(DisplayGraph.M):
            self.update()
            self.t.clear()
            self.draw(buttons=False)

        self.draw()

        self.window.onclick(self.handle_click)
        self.t.getscreen()._root.mainloop()
        #self.window.exitonclick()

    def get_vertex(self, x, y):
        """ Returns the index of the first vertex that collides with the coordinates (x,y).
        If no collision return None"""

        # Create a temporary Vertex for Vertex.distance_to
        click_location = Vertex(x, y)

        for i, v in enumerate(self.vertices):
            if v.distance_to(click_location) <= v.size:
                return i
        return None

    def select_vertex(self, i):
        self.vertices[i].selected = True

        if len(self.selected_queue) == 2:
            v = self.selected_queue.popleft()
            self.vertices[v].selected = False

        self.selected_queue.append(i)

        self.t.clear()
        self.draw()

    def handle_click(self, x, y):
        self.button_dispatch(x, y)

        vertex_index = self.get_vertex(x, y)
        if vertex_index is not None:
            self.select_vertex(vertex_index)

    def draw_dijkstra(self):
        for v in self.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.graph.dijkstra(a, b)

            for i in path:
                self.vertices[i].highlighted = True
                self.vertices[i].draw(self.t)

            self.t.clear()
            self.draw()

    def draw_a_star(self):
        for v in self.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.graph.a_star(a, b)

            for i in path:
                self.vertices[i].highlighted = True
                self.vertices[i].draw(self.t)

            self.t.clear()
            self.draw()

    def button_dispatch(self, x, y):
        for button in self.buttons:
            if x >= button.x and x <= (button.y + button.width) and y >= button.y and y <= (button.y + button.height):
                button.onclick()

    def new_graph(self):
        self.selected_queue.clear()

        V = len(self.vertices)
        E = len(self.edges)

        self.vertices = []
        self.edges = []

        self.graph = random_graph(V=V, E=E, connected=True)

        self.populate()
        self.display()

    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        denom = d if d > cls.c2 else cls.c2
        return cls.c3/denom**2


class Button(object):

    def __init__(self, x, y, text, func):
        self.x = x
        self.y = y
        self.text = text
        self.fontsize = 12
        self.height = 16
        self.width = 12 * len(self.text)
        self.onclick = func
        self.t = turtle

    def draw(self, turtle):
        turtle.up()
        turtle.setpos(self.x, self.y)
        turtle.fillcolor('gray')
        turtle.begin_fill()
        turtle.down()
        turtle.setheading(0)
        turtle.fd(self.width)
        turtle.left(90)
        turtle.fd(self.height)
        turtle.left(90)
        turtle.fd(self.width)
        turtle.left(90)
        turtle.fd(self.height)
        turtle.end_fill()

        turtle.up()
        turtle.setpos(self.x + (self.width / 2), self.y)
        turtle.write(self.text, align='center', font=('Arial', self.fontsize, 'normal'))
