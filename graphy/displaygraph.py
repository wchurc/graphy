from graphy.graph import Graph, Vertex, random_graph
from graphy import Viewer, fdag, config, fdag_imported

import math


class DisplayEdge(object):

    def __init__(self, v, w, parent, size=2):

        assert isinstance(v, DisplayVertex) and isinstance(w, DisplayVertex)

        self.v = v
        self.w = w
        self.parent = parent
        self.size = size

    def draw(self):
        self.parent.view.line(self.v.x, self.v.y, self.w.x, self.w.y,
                              color=self.color, stroke=self.size)

    @property
    def color(self):
        if self.v.highlighted and self.w.highlighted:
            return 'red'
        return 'gray'


class DisplayVertex(object):

    def __init__(self, vertex, index, parent, size=7):

        assert isinstance(vertex, Vertex)

        self.v = vertex
        self.i = index
        self.parent = parent
        self.size = size
        self._color = 'blue'
        self._marked_color = 'yellow'
        self._highlighted_color = 'red'
        self.highlighted = False
        self.selected = False

    def draw(self):
        stroke_color = 'orange' if self.selected else'black'
        self.parent.view.circle(self.x, self.y, self.size, color=self.color,
                                stroke_color=stroke_color)

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

    c1 = 5.0    # Attraction multiplier
    c2 = 30.0   # Inversely related to attraction
    c3 = 700.0  # Higher increases repulsion
    c4 = 7      # Repulsion multiplier
    M = 300     # Number of iterations

    def __init__(self, graph, width=1000, height=1000,
                 threaded=False, num_threads=4, update_algo=None):

        if not isinstance(graph, Graph):
            raise Exception("DisplayGraph must be initialized with a Graph")

        self.graph = graph

        self.components = []

        self.width = width
        self.height = height

        # Layout and display related setup
        self.size = int(math.sqrt(len(graph.vertices)))

        self.view = Viewer(width=width, height=height,
                           on_mouse_down=self.on_mouse_down,
                           on_mouse_up=self.on_mouse_up,
                           on_mouse_drag=self.on_mouse_drag)

        self.xscale = (width // 2) // self.size
        self.yscale = (height // 2) // self.size
        self.xoffset = -width // 4
        self.yoffset = -height // 4

        # Graph setup
        self.vertices = []
        self.edges = []
        self.populate()

        self.threaded = threaded
        self.num_threads = num_threads

        # Selected update method
        if update_algo == 'c_update' and fdag_imported is True:
            self.update = self.c_update
            config(self.c1, self.c2, self.c3, self.c4,
                   self.threaded, self.num_threads)
        else:
            self.update = self.python_update

    def on_mouse_down(self, x, y):
        for component in self.components:
            component.on_mouse_down(x, y)

    def on_mouse_up(self, x, y):
        for component in self.components:
            component.on_mouse_up(x, y)

    def on_mouse_drag(self, x, y):
        for component in self.components:
            component.on_mouse_drag(x, y)

    def populate(self):

        x, y = 0, 0

        # Create DisplayVertices
        for i, v in enumerate(self.graph.vertices):
            v.x = (x * self.xscale) + self.xoffset
            v.y = (y * self.yscale) + self.yoffset
            self.vertices.append(DisplayVertex(v, i, self))

            x += 1
            if x >= self.size:
                x = 0
                y += 1

        # Create DisplayEdges
        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(DisplayEdge(self.vertices[i],
                                                  self.vertices[w], self))

    def c_update(self):
        verts = [(float(self.vertices[x].x), float(self.vertices[x].y))
                 for x in range(len(self.vertices))]

        edges = [(int(self.edges[x].v.i), int(self.edges[x].w.i))
                 for x in range(len(self.edges))]

        new_vertices = fdag(verts, len(verts), edges, len(edges))

        for i, new_vert in enumerate(new_vertices):
            self.vertices[i].x, self.vertices[i].y = new_vert

    def python_update(self):
        for v in self.vertices:
            for w in self.vertices:
                if w is not v:
                    d = v.distance_to(w)
                    f = self.repulsion(d) * DisplayGraph.c4
                    x, y = [f*x for x in w.unit_to(v)]
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

        self.view.clear()

        for e in self.edges:
            e.draw()

        for v in self.vertices:
            v.draw()

        self.view.update(draw_buttons=buttons)

    def display(self, run=True):

        for x in range(DisplayGraph.M):
            self.update()
            self.draw(buttons=False)

        self.draw()

        # Run the mainloop to prevent window from closing
        if run:
            self.view.run()

    def new_graph(self):

        V = len(self.vertices)
        E = len(self.edges)

        self.vertices = []
        self.edges = []

        self.graph = random_graph(V=V, E=E, connected=True)

        self.populate()

        for component in self.components:
            component.reset()

        self.display(run=False)

    def get_vertex(self, x, y):
        """Returns the index of the first vertex that collides with the
        coordinates (x,y). If no collision return None"""

        # Create a temporary Vertex for Vertex.distance_to
        click_location = Vertex(x, y)

        for i, v in enumerate(self.vertices):
            if v.distance_to(click_location) <= v.size:
                return i
        return None

    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        denom = d if d > cls.c2 else cls.c2
        return cls.c3/denom**2
