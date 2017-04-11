import turtle

from viewer import Viewer


class TurtleViewer(Viewer):
    def __init__(self, on_click=None):
        self.window = turtle.Screen()
        self.window.tracer(0, 0)
        self.t = turtle.Turtle(visible=False)
        self.t.speed(0)
        self._buttons = []

        self.width = self.window.window_width()
        self.height = self.window.window_height()

        self._on_click = on_click
        # Tell turtle how to handle clicks
        self.window.onclick(self._handle_click)

        # Default values
        self.fill_col = 'blue'
        self.stroke_col = 'black'
        self.stroke = 2

    def circle(self, x, y, radius, **config):
        self.t.up()
        self.t.setpos(x + radius, y)
        self.t.setheading(90)
        self.t.down()
        color = config.get('color') or self.fill_col
        self.t.fillcolor(color)
        stroke = config.get('stroke') or self.stroke
        self.t.pensize(stroke)
        stroke_color = config.get('stroke_color') or self.stroke_col
        self.t.pencolor(stroke_color)
        self.t.begin_fill()
        self.t.circle(radius)
        self.t.end_fill()
        #t.dot(self.size, self.color)

    def line(self, x1, y1, x2, y2, **config):
        color = config.get('color') or self.stroke_col
        self.t.color(color)

        weight = config.get('weight') or self.stroke
        self.t.pensize(weight)

        self.t.up()
        self.t.setpos(x1, y1)
        self.t.down()
        self.t.setpos(x2, y2)

    def clear(self):
        self.t.clear()

    def update(self, draw_buttons=True):
        if draw_buttons:
            for button in self._buttons:
                button.draw(self.t)
        self.window.update()

    def run(self):
        self.t.getscreen()._root.mainloop()

    def add_button(self, button):
        button.t = self.t
        self._buttons.append(button)

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

        def draw(self, turtle):
            self.t.up()
            self.t.setpos(self.x, self.y)
            self.t.fillcolor('gray')
            self.t.begin_fill()
            self.t.down()
            self.t.setheading(0)
            self.t.fd(self.width)
            self.t.left(90)
            self.t.fd(self.height)
            self.t.left(90)
            self.t.fd(self.width)
            self.t.left(90)
            self.t.fd(self.height)
            self.t.end_fill()

            self.t.up()
            self.t.setpos(self.x + (self.width / 2), self.y)
            self.t.write(self.text, align='center', font=('Arial', self.fontsize, 'normal'))

    def button_dispatch(self, x, y):
        for button in self._buttons:
            if x >= button.x and x <= (button.y + button.width) and \
               y >= button.y and y <= (button.y + button.height):
                button.onclick()

    def _handle_click(self, x, y):
        self.button_dispatch(x, y)

        # Pass click coordinates to client code
        if self._on_click:
            self._on_click(x, y)

