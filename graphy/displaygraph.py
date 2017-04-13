from collections import deque
import math

from graphy.graph import Graph, Edge, Vertex, random_graph
from graphy.pygame_viewer import PygameViewer

try:
    from fdag import fdag, config
except ImportError:
    fdag_imported = False
    print("Failed to import fdag. C-extensions are disabled")
else:
    fdag_imported = True


class DisplayEdge(object):

    def __init__(self, v, w, view):

        assert isinstance(v, DisplayVertex) and isinstance(w, DisplayVertex)

        self.v = v
        self.w = w
        self.view = view
        self.size = 2

    def draw(self):
        self.view.line(self.v.x, self.v.y, self.w.x, self.w.y,
                  color=self.color, stroke=self.size)

    @property
    def color(self):
        if self.v.highlighted and self.w.highlighted:
            return 'red'
        return 'gray'


class DisplayVertex(object):

    def __init__(self, vertex, index, view):

        assert isinstance(vertex, Vertex)

        self.v = vertex
        self.i = index
        self.view = view
        self.size = 7
        self._color = 'blue'
        self._marked_color = 'yellow'
        self._highlighted_color = 'red'
        self.highlighted = False
        self.selected = False

    def draw(self):
        stroke_color = 'orange' if self.selected else'black'
        self.view.circle(self.x, self.y, self.size, color=self.color,
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

        self.width = width
        self.height = height

        # Layout and display related setup
        self.size = int(math.sqrt(len(graph.vertices)))

        self.view = PygameViewer(width=width, height=height, on_click=self.handle_click)

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
            config(self.c1, self.c2, self.c3, self.c4, self.threaded, self.num_threads)
        else:
            self.update = self.python_update

    def handle_click(self):
        pass

    def populate(self):

        x, y = 0, 0

        # Create DisplayVertices
        for i, v in enumerate(self.graph.vertices):
            v.x = (x * self.xscale) + self.xoffset
            v.y = (y * self.yscale) + self.yoffset
            self.vertices.append(DisplayVertex(v, i, self.view))

            x += 1
            if x >= self.size:
                x = 0
                y += 1

        # Create DisplayEdges
        for i, v in enumerate(self.graph.vertices):
            for w in v:
                if w > i:
                    self.edges.append(DisplayEdge(self.vertices[i], self.vertices[w], self.view))

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
                    #delta = math.sqrt(x**2 + y**2)
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
        self.selected_queue.clear()

        V = len(self.vertices)
        E = len(self.edges)

        self.vertices = []
        self.edges = []

        self.graph = random_graph(V=V, E=E, connected=True)

        self.populate()
        self.display(run=False)

    @classmethod
    def attraction(cls, d):
        return cls.c1 * math.log10(d/cls.c2)

    @classmethod
    def repulsion(cls, d):
        denom = d if d > cls.c2 else cls.c2
        return cls.c3/denom**2


class ShortestPathGraph(DisplayGraph):

    def __init__(self, *args, **kwargs):
        super(ShortestPathGraph, self).__init__(*args, **kwargs)

        # Initialize queue for selected vertices
        self.selected_queue = deque(maxlen=2)

    def handle_click(self, x, y):
        vertex_index = self.get_vertex(x, y)
        if vertex_index is not None:
            self.select_vertex(vertex_index)

    def get_vertex(self, x, y):
        """Returns the index of the first vertex that collides with the coordinates (x,y).
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

        self.draw()

    def display_path(self, path):
        # Highlight path vertices
        for i in path:
            self.vertices[i].highlighted = True
            self.vertices[i].draw()

        self.draw()

    def draw_dijkstra(self):
        # Clear any previous highlighted vertices
        for v in self.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.graph.dijkstra(a, b)

            self.display_path(path)

    def draw_a_star(self):
        # Clear any previous highlighted vertices
        for v in self.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.graph.a_star(a, b)

            self.display_path(path)
