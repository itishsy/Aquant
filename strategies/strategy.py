from datetime import datetime
from storage.db import db, find_active_symbols
from abc import ABC, abstractmethod
from entities.candle import Candle
from entities.signal import Signal
from enums.entity import Entity
from typing import List
import signals.signals as sig

factory = {}


def register_strategy(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Strategy(ABC):
    signals = []
    codes = []
    begin = None
    klt = 101
    limit = 100

    def search_all(self):
        session = db.get_session(Entity.Signal)

        if len(self.codes) == 0:
            symbols = find_active_symbols()
            for sym in symbols:
                self.codes.append(sym.code)

        for code in self.codes:
            print('[{}] [{}] [{}] searching...'.format(datetime.now(), code, self.__class__.__name__))
            self.search(code)

        if len(self.signals) > 0:
            session.add_all(self.signals)
            session.commit()
            print('[{}] [{}] signals: {}'.format(datetime.now(), self.__class__.__name__, len(self.signals)))
            self.signals.clear()

    def append_signals(self, code, candles: List[Candle]):
        if len(candles) > 0:
            cds = sig.divergence(candles)
            for cd in cds:
                si = Signal(dt=cd.dt, klt=self.klt, type=self.__class__.__name__, value=cd.klt)
                si.code = code
                si.notify = 0
                si.created = datetime.now()
                self.signals.append(si)

    def child_klt(self):
        if self.klt == 101:
            return [60, 30, 15]
        elif self.klt == 102:
            return [101, 60]
        elif self.klt == 60:
            return [15, 5]
        elif self.klt == 30:
            return [5]
        else:
            return []

    def parent_klt(self):
        if self.klt == 101:
            return 102
        elif self.klt in [30, 60]:
            return 101
        elif self.klt == 15:
            return 60
        elif self.klt == 5:
            return 30
        else:
            return []

    @abstractmethod
    def search(self, code):
        pass
