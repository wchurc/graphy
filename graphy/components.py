from graphy.displaygraph import DisplayGraph

from collections import deque


class Component(object):

    def on_mouse_down(self, x, y):
        pass

    def on_mouse_up(self, x, y):
        pass

    def on_mouse_drag(self, x, y):
        pass

    def reset(self):
        pass


class Pathfinder(Component):

    def __init__(self, display_graph):
        self.dg = display_graph
        # Initialize queue for selected vertices
        self.selected_queue = deque(maxlen=2)

    def on_mouse_down(self, x, y):
        vertex_index = self.dg.get_vertex(x, y)
        if vertex_index is not None:
            self.select_vertex(vertex_index)

    def select_vertex(self, i):
        self.dg.vertices[i].selected = True

        if len(self.selected_queue) == 2:
            v = self.selected_queue.popleft()
            self.dg.vertices[v].selected = False

        self.selected_queue.append(i)

        self.dg.draw()

    def display_path(self, path):
        # Highlight path vertices
        for i in path:
            self.dg.vertices[i].highlighted = True
            self.dg.vertices[i].draw()

        self.dg.draw()

    def draw_dijkstra(self):
        # Clear any previous highlighted vertices
        for v in self.dg.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.dg.graph.dijkstra(a, b)

            self.display_path(path)

    def draw_a_star(self):
        # Clear any previous highlighted vertices
        for v in self.dg.vertices:
            v.v.marked = False
            v.highlighted = False
            v.selected = False

        if len(self.selected_queue) == 2:
            a, b = iter(self.selected_queue)
            path = self.dg.graph.a_star(a, b)

            self.display_path(path)

    def reset(self):
        self.selected_queue.clear()


class Dragger(Component):

    def __init__(self, display_graph):
        self.held_vertex = None
        self.dg = display_graph
        self.tick = 0
        self.tick_max = 4

    def on_mouse_down(self, x, y):
        vertex_index = self.dg.get_vertex(x, y)
        if vertex_index is not None:
            self.lengths = [e.v.distance_to(e.w) for e in self.dg.edges]
            self.held_vertex = vertex_index

    def on_mouse_up(self, x, y):
        if self.held_vertex is not None:
            self.held_vertex = None

    def on_mouse_drag(self, x, y):
        self.tick += 1
        if self.held_vertex is not None and self.tick > self.tick_max:
            self.relax(self.dg.vertices[self.held_vertex], (x, y))
            self.dg.draw()
            self.tick = 0

    def relax(self, vertex, newpos):

        vertex.x, vertex.y = newpos

        for i, e in enumerate(self.dg.edges):
            rest_len = self.lengths[i]
            delta = (e.w.x - e.v.x, e.w.y - e.v.y)
            delta_len = e.w.distance_to(e.v)
            diff = (delta_len - rest_len)/delta_len
            e.w.x -= delta[0]*0.5*diff
            e.w.y -= delta[1]*0.5*diff
            e.v.x += delta[0]*0.5*diff
            e.v.y += delta[1]*0.5*diff
