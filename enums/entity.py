from enum import Enum


class Entity:
    Symbol = "symbol"
    Signal = "signal"

    def __str__(self):
        return self.value
