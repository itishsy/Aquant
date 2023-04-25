from enum import Enum


class Direction(Enum):
    Up = "向上"
    Down = "向下"

    def __str__(self):
        return self.value
