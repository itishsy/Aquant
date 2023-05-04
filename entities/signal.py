from dataclasses import dataclass


@dataclass
class Signal:
    def __init__(self, dt, type, value):
        self.dt = dt
        self.type = type
        self.value = value

    id: int
    code: str
    dt: str
    klt: int
    type: str
    value: int
    notify: int = 0
