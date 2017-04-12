import pygame
from pygame.locals import *

from viewer import Viewer


class PygameViewer(Viewer):
    def __init__(self, *args, **kwargs):
        super(PygameViewer, self).__init__(*args, **kwargs)
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))
        self.colors = {'blue': (0, 0, 255), 'red': (255, 0, 0),
                       'yellow': (100, 100, 0), 'gray': (100, 100, 100),
                       'black': (0, 0, 0), 'white': (255, 255, 255),
                       'orange': (200, 100, 0)}
        # Default values
        self.fill_col = self.colors.get('blue')
        self.clear_col = self.colors.get('white')
        self.stroke_col = self.colors.get('gray')
        self.stroke = 2

    def get_color(self, config, keyword):
        color = config.get(keyword)
        if color:
            return self.colors.get(color) or self.fill_col
        else:
            return self.fill_col

    def circle(self, x, y, radius, **config):
        color = self.get_color(config, 'color')
        x = int(x + self.width/2)
        y = int(y + self.height/2)
        pygame.draw.circle(self.window, color, (x, y), radius)
        if config.get('stroke_color'):
            stroke = config.get('stroke') or 2
            stroke_color = self.get_color(config, 'stroke_color')
            pygame.draw.circle(self.window, stroke_color, (x, y), radius, stroke)

    def line(self, x1, y1, x2, y2, **config):
        color = self.get_color(config, 'color')
        stroke = config.get('weight') or self.stroke
        x1 = int(x1 + self.width/2)
        y1 = int(y1 + self.height/2)
        x2 = int(x2 + self.width/2)
        y2 = int(y2 + self.height/2)
        pygame.draw.line(self.window, color, (x1, y1), (x2, y2), stroke)

    def rect(self, x1, y1, width, height, **config):
        color = self.get_color(config, 'color')
        pygame.draw.rect(self.window, color, Rect((x1, y1), (width, height)))

    def clear(self):
        self.window.fill(self.clear_col)

    def update(self, **kwargs):
        pygame.display.update()

    def run(self):
        while True:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                if self._on_click is not None:
                    # Translate to -x,-y,+x,+y coordinate grid
                    x, y = event.pos[0] - self.width/2, event.pos[1] - self.height/2
                    self._on_click(x, y)
                    #self.update()
            if event.type == QUIT:
                pygame.quit()

    def add_button(self, button):
        pass
