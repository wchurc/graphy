from functools import partial
import turtle

from viewer import Viewer


class TurtleViewer(Viewer):
    def __init__(self, width, height, on_click=None):
        self.window = turtle.Screen()
        self.window.setup(width=width, height=height)
        self.window.tracer(0, 0)
        self.t = turtle.Turtle(visible=False)
        self.t.speed(0)
        self._buttons = []

        self.width = width
        self.height = height

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
                button.draw()
        self.window.update()

    def run(self):
        self.t.getscreen()._root.mainloop()

    def add_button(self, button):
        button.t = self.t
        button.draw = partial(self.draw_button, button, self.t)
        self._buttons.append(button)

    @staticmethod
    def draw_button(btn, turtle):
        btn.t.up()
        btn.t.setpos(btn.x, btn.y)
        btn.t.fillcolor('gray')
        btn.t.begin_fill()
        btn.t.down()
        btn.t.setheading(0)
        btn.t.fd(btn.width)
        btn.t.left(90)
        btn.t.fd(btn.height)
        btn.t.left(90)
        btn.t.fd(btn.width)
        btn.t.left(90)
        btn.t.fd(btn.height)
        btn.t.end_fill()

        btn.t.up()
        btn.t.setpos(btn.x + (btn.width / 2), btn.y)
        btn.t.write(btn.text, align='center', font=('Arial', btn.fontsize, 'normal'))


    def _handle_click(self, x, y):
        self.button_dispatch(x, y)

        # Pass click coordinates to client code
        if self._on_click:
            self._on_click(x, y)
