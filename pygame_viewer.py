from functools import partial

import pygame
from pygame.locals import MOUSEBUTTONDOWN, QUIT, Rect

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

    def translate(self, x, y):
        """Translate from the range ((-x,-y)->(x, y)) to ((0, 0)->(2x, 2y))
        and flip the y dimension"""
        return int(x + self.width/2), int(self.height - (y + self.height/2))

    def translate_back(self, x, y):
        return int(x - self.width/2), int(self.height/2 - y)

    def get_color(self, config, keyword):
        color = config.get(keyword)
        if color:
            return self.colors.get(color) or self.fill_col
        else:
            return self.fill_col

    def circle(self, x, y, radius, **config):
        color = self.get_color(config, 'color')
        x, y = self.translate(x, y)
        pygame.draw.circle(self.window, color, (x, y), radius)
        if config.get('stroke_color'):
            stroke = config.get('stroke') or 2
            stroke_color = self.get_color(config, 'stroke_color')
            pygame.draw.circle(self.window, stroke_color, (x, y), radius, stroke)

    def line(self, x1, y1, x2, y2, **config):
        color = self.get_color(config, 'color')
        stroke = config.get('weight') or self.stroke
        x1, y1 = self.translate(x1, y1)
        x2, y2 = self.translate(x2, y2)
        pygame.draw.line(self.window, color, (x1, y1), (x2, y2), stroke)

    def rect(self, x, y, width, height, **config):
        x, y = self.translate(x, y)
        color = self.get_color(config, 'color')
        pygame.draw.rect(self.window, color, Rect((x, y - height), (width, height)))

    def clear(self):
        self.window.fill(self.clear_col)

    def update(self, **kwargs):
        for button in self._buttons:
            button.draw()
        pygame.display.update()

    def run(self):
        while True:
            event = pygame.event.wait()
            if event.type == MOUSEBUTTONDOWN:
                if self._on_click is not None:
                    # Translate to -x,-y,+x,+y coordinate grid
                    x, y = self.translate_back(event.pos[0], event.pos[1])
                    self.button_dispatch(x, y)
                    self._on_click(x, y)
                    # TODO -> calling self._on_click here creates recursive call to self.run
            if event.type == QUIT:
                pygame.quit()

    def draw_button(self, button):
        self.rect(button.x, button.y, button.width, button.height, stroke=2)
        x, y = self.translate(button.x, button.y)
        offset = (button.width - button.label.get_size()[0]) / 2
        self.window.blit(button.label, (x + offset, y - button.height))

    def add_button(self, button):
        button.draw = partial(self.draw_button, button)
        self._buttons.append(button)
        button.font = pygame.font.SysFont("monospace", button.fontsize)
        button.label = button.font.render(button.text, 1, (255, 255, 255))
