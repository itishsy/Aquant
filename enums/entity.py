from enum import Enum


class Entity:
    Symbol = "symbol"
    Single = "single"

    def __str__(self):
        return self.value
