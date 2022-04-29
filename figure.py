import random

from shape import *
from tetris_util import colors

shapes: List[Shape] = [
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
		self.type = random.randint(6, 6)
		self.color = shapes[self.type].color()
		self.rotation = 0

	def image(self):
		return shapes[self.type].rotation(self.rotation)

	def rotate(self):
		self.rotation = (self.rotation + 1) % shapes[self.type].rotation_count()

	def width(self) -> int:
		return shapes[self.type].width()

	def height(self) -> int:
		return shapes[self.type].height()

	def x_adjusted(self) -> int:
		return self.x + shapes[self.type].offset_x(self.rotation)

	def y_adjusted(self) -> int:
		return self.y + shapes[self.type].offset_y(self.rotation)

	def __eq__(self, other):
		if not isinstance(other, Figure):
			# don't attempt to compare against unrelated types
			return NotImplemented

		return self.type == other.type and self.rotation == other.rotation \
			   and self.x == other.x and self.y == other.y
