class Shape:

    def __init__(self, rotations: list[list[int]], width: int, height: int):
        self.__rotations = rotations
        self.__width = width
        self.__height = height

    def height(self) -> int:
        return self.__height

    def width(self) -> int:
        return self.__width

    def rotation(self, index: int) -> list[int]:
        return self.__rotations[index]

    def rotation_count(self) -> int:
        return len(self.__rotations)


BLOCK = Shape([[1, 2, 5, 6]], 2, 2)
T = Shape([[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]], 3, 2)
L_LEFT = Shape([[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]], 2, 3)
L_RIGHT = Shape([[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]], 2, 3)
Z = Shape([[4, 5, 9, 10], [2, 6, 5, 9]], 3, 2)
Z_INVERSE = Shape([[5, 6, 8, 9], [0, 4, 5, 9]], 3, 2)
#Z_INVERSE = Shape([[6, 7, 9, 10], [1, 5, 6, 10]], 3, 2)
LINE = Shape([[1, 5, 9, 13], [4, 5, 6, 7]], 1, 4)
