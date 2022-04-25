from typing import List


class Rotation:

	def __init__(self, rotation_arr, offset_x, offset_y):
		self.rotation_arr = rotation_arr
		self.offset_x = offset_x
		self.offset_y = offset_y


class Shape:

	def __init__(self, rotations: List[Rotation], width: int, height: int, color: int):
		self.__rotations = rotations
		self.__width = width
		self.__height = height
		self.__color = color

	def height(self) -> int:
		return self.__height

	def width(self) -> int:
		return self.__width

	def color(self) -> int:
		return self.__color

	def rotation(self, index: int) -> List[int]:
		return self.__rotations[index].rotation_arr

	def offset_x(self, index) -> int:
		return self.__rotations[index].offset_x

	def offset_y(self, index) -> int:
		return self.__rotations[index].offset_y

	def rotation_count(self) -> int:
		return len(self.__rotations)


BLOCK = Shape([Rotation([1, 2, 5, 6], 1, 0)], 2, 2, 1)
T = Shape([Rotation([1, 4, 5, 6], 0, 0), Rotation([1, 4, 5, 9], 0, 0), Rotation([4, 5, 6, 9], 0, 1), Rotation([1, 5, 6, 9], 1, 0)], 3, 2, 2)
L_LEFT = Shape([Rotation([1, 2, 6, 10], 1, 0), Rotation([5, 6, 7, 9], 1, 1), Rotation([2, 6, 10, 11], 2, 0), Rotation([3, 5, 6, 7], 1, 0)], 2, 3, 3)
L_RIGHT = Shape([Rotation([1, 2, 5, 9], 1, 0), Rotation([0, 4, 5, 6], 0, 0), Rotation([1, 5, 9, 8], 0, 0), Rotation([4, 5, 6, 10], 0, 1)], 2, 3, 4)
Z = Shape([Rotation([4, 5, 9, 10], 0, 1), Rotation([2, 6, 5, 9], 1, 0)], 3, 2, 5)
Z_INVERSE = Shape([Rotation([5, 6, 8, 9], 0, 1), Rotation([0, 4, 5, 9], 0, 0)], 3, 2, 6)
LINE = Shape([Rotation([1, 5, 9, 13], 1, 0), Rotation([4, 5, 6, 7], 0, 1)], 1, 4, 7)
