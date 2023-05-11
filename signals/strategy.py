import datetime

from storage.db import db, find_candles, find_active_symbols
from storage.fetcher import fetch_data
from abc import ABC, abstractmethod
from entities.candle import Candle
from entities.signal import Signal
from entities.symbol import Symbol
from enums.entity import Entity
from typing import List

factory = {}


def register_strategy(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Strategy(ABC):
    code = None
    begin = None
    klt = 101

    def search_all(self):
        symbols = find_active_symbols()
        if len(symbols) == 0:
            return
        session = db.get_session(Entity.Signal)
        signals = []
        if self.code is not None:
            sis = self.search_signal(fetch_data(self.code, self.klt, self.begin))
            self.append_signals(signals,sis)
        else:
            for sb in symbols:
                self.code = sb.code
                sis = self.search_signal(find_candles(sb.code, self.klt, limit=100))
                self.append_signals(signals,sis)

        if len(signals) > 0:
            session.add_all(signals)
            session.commit()

    def append_signals(self, signals: List[Signal], sis: List[Signal]):
        if len(sis) > 0:
            for si in sis:
                si.code = self.code
                if si.klt is None:
                    si.klt = self.klt
                si.notify = 0
                si.created = datetime.datetime.now()
                signals.append(si)

    @abstractmethod
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        pass
