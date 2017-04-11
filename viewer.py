from abc import ABCMeta, abstractmethod


class Viewer(object, metaclass=ABCMeta):
    def __init__(self, width, height, on_click=None):
        self.width = width
        self.height = height
        self._on_click = on_click

        self._buttons = []

    @abstractmethod
    def circle():
        pass

    @abstractmethod
    def line():
        pass

    @abstractmethod
    def clear():
        pass

    @abstractmethod
    def update():
        pass

    @abstractmethod
    def run():
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
