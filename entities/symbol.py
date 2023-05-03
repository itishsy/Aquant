from dataclasses import dataclass


@dataclass
class Symbol:
    def __init__(self, series=None):
        if series is not None:
            for key in series.keys():
                setattr(self, key, series[key])

    id: int
    code: str
    name: str
    status: int
    comment: str
