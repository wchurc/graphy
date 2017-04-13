from functools import partial

import pygame
from pygame.locals import MOUSEBUTTONDOWN, QUIT, Rect

from viewer import Viewer


class PygameViewer(Viewer):
    def __init__(self, *args, **kwargs):
        super(PygameViewer, self).__init__(*args, **kwargs)
        # Initialize pygame
        pygame.init()
        self.window = pygame.display.set_mode((self.width, self.height))

        # Dict for translating colors from strings to RGB tuples
        self.colors = {'blue': (0, 0, 255), 'red': (255, 0, 0),
                       'yellow': (255, 255, 0), 'gray': (100, 100, 100),
                       'black': (0, 0, 0), 'white': (255, 255, 255),
                       'orange': (255, 165, 0)}

        # Default values
        self.fill_col = self.colors.get('blue')
        self.clear_col = self.colors.get('white')
        self.stroke_col = self.colors.get('gray')
        self.stroke = 2

    def _translate(self, x, y):
        """Translate between coordinate systems and flip the y dimension.
        ((-x,-y)->(x, y)) to ((0, 0)->(2x, 2y))
        """
        return int(x + self.width/2), int(self.height - (y + self.height/2))

    def _translate_back(self, x, y):
        """Translate between coordinate systems and flip the y dimension.
        ((0, 0)->(2x, 2y)) to ((-x,-y)->(x, y))
        """
        return int(x - self.width/2), int(self.height/2 - y)

    def _get_color(self, config, keyword):
        """Returns an RGB tuple. Will return default value if the config dict
        doesn't the supplied keyword or if the requested color isn't known.
        """
        color = config.get(keyword)
        if color:
            return self.colors.get(color) or self.fill_col
        else:
            return self.fill_col

    def circle(self, x, y, radius, **config):
        color = self._get_color(config, 'color')
        x, y = self._translate(x, y)

        # Draw the circle fill
        pygame.draw.circle(self.window, color, (x, y), radius)

        # Draw a stroke if necessary
        if config.get('stroke_color'):
            stroke = config.get('stroke') or self.stroke
            stroke_color = self._get_color(config, 'stroke_color')
            pygame.draw.circle(self.window, stroke_color, (x, y), radius, stroke)

    def line(self, x1, y1, x2, y2, **config):
        color = self._get_color(config, 'color')
        stroke = config.get('weight') or self.stroke

        x1, y1 = self._translate(x1, y1)
        x2, y2 = self._translate(x2, y2)

        pygame.draw.line(self.window, color, (x1, y1), (x2, y2), stroke)

    def rect(self, x, y, width, height, **config):
        x, y = self._translate(x, y)
        color = self._get_color(config, 'color')

        pygame.draw.rect(self.window, color, Rect((x, y - height), (width, height)))

    def clear(self):
        self.window.fill(self.clear_col)

    def update(self, **kwargs):
        for button in self._buttons:
            button.draw()
        pygame.display.update()

    def run(self):
        while True:
            # Block until there is an event
            event = pygame.event.wait()

            if event.type == MOUSEBUTTONDOWN:
                if self._on_click is not None:
                    # Translate to -x,-y,+x,+y coordinate grid
                    x, y = self._translate_back(event.pos[0], event.pos[1])
                    self.button_dispatch(x, y)

                    # TODO -> calling self._on_click here creates recursive call to self.run
                    self._on_click(x, y)

            if event.type == QUIT:
                pygame.quit()

    def draw_button(self, button):
        self.rect(button.x, button.y, button.width, button.height, stroke=2)
        x, y = self._translate(button.x, button.y)
        offset = (button.width - button.label.get_size()[0]) / 2
        self.window.blit(button.label, (x + offset, y - button.height))

    def add_button(self, button):
        button.draw = partial(self.draw_button, button)
        self._buttons.append(button)
        button.font = pygame.font.SysFont("monospace", button.fontsize)
        button.label = button.font.render(button.text, 1, (255, 255, 255))
