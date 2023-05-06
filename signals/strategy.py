from storage.db import db, find_candles, find_active_symbols
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
    reverse = "反转",
    rising = "持续上涨"
    gold_cross = "零轴上方金叉",
    reverse_to_gold_cross = "（次级别）反转形成金叉",
    gold_cross_from_reverse = "反转后的金叉"

    __klt = 101

    def klt(self, klt):
        self.__klt = klt

    def search_all(self):
        symbols = find_active_symbols()
        if len(symbols) == 0:
            return
        session = db.get_session(Entity.Signal)
        signals = []
        for sb in symbols:
            sgs = self.search_signal(find_candles(sb.code, self.__klt, limit=100))
            if len(sgs) > 0:
                for sgn in sgs:
                    sgn.code = sb.code
                    sgn.klt = self.__klt
                    signals.append(sgn)
        if len(signals) > 0:
            session.add_all(signals)
            session.commit()

    @abstractmethod
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        pass
