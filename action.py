from enum import Enum

ACTION_SPACE_SIZE = 5

class Action(Enum):
    ROTATE = 0
    FAST_DROP = 1
    MOVE_LEFT = 2
    MOVE_RIGHT = 3
    INSTANT_DROP = 4
    NOTHING = 5


