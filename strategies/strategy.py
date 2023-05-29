from datetime import datetime
from storage.db import db, find_active_symbols
from abc import ABC, abstractmethod
from entities.candle import Candle
from entities.signal import Signal
from enums.entity import Entity
from typing import List
from sqlalchemy import select, desc, and_, text
import signals.utils as sig

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
    freq = 101
    limit = 100

    def search_all(self):
        try:
            session = db.get_session(Entity.Signal)

            if len(self.codes) == 0:
                symbols = find_active_symbols()
                for sym in symbols:
                    self.codes.append(sym.code)

            i = 1
            for code in self.codes:
                print('[{}] [{}] [{}] searching... {}'.format(datetime.now(), code, self.__class__.__name__, i))
                self.search(code)
                if len(self.signals) > 0:
                    session.add_all(self.signals)
                    session.commit()
                    print('[{}] [{}] signals: {}'.format(datetime.now(), self.__class__.__name__, len(self.signals)))
                    self.signals.clear()
                i = i + 1
        except Exception as e:
            print(e)

    def append_signals(self, code, candles: List[Candle]):
        if len(candles) > 0:
            cds = sig.divergence(candles)
            for cd in cds:
                si = Signal(dt=cd.dt, freq=self.freq, type=self.__class__.__name__, value=cd.freq)
                si.code = code
                si.created = datetime.now()
                self.signals.append(si)

    def upset_signals(self, signals: List[Signal]):
        if len(signals) > 0:
            session = db.get_session(Entity.Signal)
            for signal in signals:
                session.query()
                clauses = and_(Signal.code == signal.code, Signal.type == signal.type, Signal.dt == signal.dt, Signal.freq == signal.freq)
                sgs = session.execute(
                    select(Signal).where(clauses)
                ).scalars().fetchall()
                if sgs is None or len(sgs) == 0:
                    self.signals.append(signal)

    def child_freq(self, freq=None):
        if freq is None:
            freq = self.freq
        if freq == 101:
            return [60, 30]
        elif freq == 102:
            return [101]
        elif freq == 60:
            return [15]
        elif freq == 30:
            return [5]
        else:
            return [1]

    def grandchild_freq(self, freq=None):
        ks = self.child_freq(freq)
        cck = []
        for k in ks:
            cks = self.child_freq(k)
            for ck in cks:
                if ck not in cck:
                    cck.append(ck)
        return cck

    def parent_freq(self, freq=None):
        if freq is None:
            freq = self.freq
        if freq == 101:
            return 102
        elif freq in [30, 60]:
            return 101
        elif freq == 15:
            return 60
        elif freq == 5:
            return 30
        else:
            return 5

    @abstractmethod
    def search(self, code):
        pass
