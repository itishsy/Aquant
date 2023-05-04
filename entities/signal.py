from dataclasses import dataclass


@dataclass
class Signal:
    id: int
    code: str
    dt: str
    klt: int
    type: str
    value: int
    notify: int = 0
