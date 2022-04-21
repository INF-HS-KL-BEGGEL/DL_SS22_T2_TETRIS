from enum import Enum

class Action(Enum):
    ROTATE = 1
    FAST_DROP = 2
    MOVE_LEFT = 3
    MOVE_RIGHT = 4
    INSTANT_DROP = 5
    NOTHING = 6