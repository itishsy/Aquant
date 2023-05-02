from dataclasses import dataclass


@dataclass
class Signal:
    code: str
    dt: str
    klt: int
    type: str
    value: int
