import random

from shape import *
from tetris_util import colors

figures: list[Shape] = [
    LINE,
    Z,
    Z_INVERSE,
    L_RIGHT,
    L_LEFT,
    T,
    BLOCK,
]


class Figure:
    x = 0
    y = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.type = random.randint(0, len(figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return figures[self.type].rotation(self.rotation)

    def rotate(self):
        self.rotation = (self.rotation + 1) % figures[self.type].rotation_count()

    def width(self) -> int:
        return figures[self.type].width()

    def height(self) -> int:
        return figures[self.type].height()
