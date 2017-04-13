from abc import ABCMeta, abstractmethod
from functools import partial


class Viewer(object, metaclass=ABCMeta):
    """Abstract base class for drawing primitives, managing buttons,
    and handling mouse events."""
    def __init__(self, width=1000, height=1000, on_click=None):
        """width and height are the width and height of the window to be
        created. on_click is a function that takes x and y parameters to be
        called when a mouse click event happens."""
        self.width = width
        self.height = height
        self._on_click = on_click

        self._buttons = []

    @abstractmethod
    def circle(self, x, y, radius, **config):
        """Draw a circle at position (x, y) with the given radius"""
        pass

    @abstractmethod
    def line(self, x1, y1, x2, y2, **config):
        """Draw a line from (x1, y1) to (x2, y2)"""
        pass

    @abstractmethod
    def clear(self):
        """Clear the window"""
        pass

    @abstractmethod
    def update(self):
        """Update the window"""
        pass

    @abstractmethod
    def run():
        """Start the event loop"""
        pass

    @abstractmethod
    def add_button():
        pass

    class Button(object):

        def __init__(self, x, y, text, func):
            self.x = x
            self.y = y
            self.text = text
            self.fontsize = 12
            self.height = 16
            self.width = 12 * len(self.text)
            self.onclick = func
            self.t = None

        def draw(self):
            pass

    def button_dispatch(self, x, y):
        for button in self._buttons:
            if x >= button.x and x <= (button.y + button.width) and \
               y >= button.y and y <= (button.y + button.height):
                button.onclick()