from enum import Enum


class Strategy(Enum):
    Reverse = "反转"

    def __str__(self):
        return self.value
