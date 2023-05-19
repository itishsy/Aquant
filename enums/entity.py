from enum import Enum


class Entity:
    Symbol = "symbol"
    Signal = "signal"
    Ticket = "ticket"

    def __str__(self):
        return self.value
