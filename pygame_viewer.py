from viewer import Viewer


class PygameViewer(Viewer):
    def __init__(self, *args, **kwargs):
        super(PygameViewer, self).__init(args, kwargs)

    def circle(self, x, y, radius, **config):
        pass

    def line(self, x1, y1, x2, y2, **config):
        pass

    def clear(self):
        pass

    def update(self):
        pass

    def run(self):
        pass

    def add_button(self, button):
        pass
