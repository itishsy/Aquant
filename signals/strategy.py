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
    reverse = "反转",
    rising = "持续上涨"
    gold_cross = "零轴上方金叉",
    reverse_to_gold_cross = "（次级别）反转形成金叉",
    gold_cross_from_reverse = "反转后的金叉"

    __klt = 101
    __code = None
    __begin = None

    def klt(self, klt, code=None, begin=None):
        self.__klt = klt
        self.__code = code
        self.__begin = begin

    def search_all(self):
        symbols = find_active_symbols()
        if len(symbols) == 0:
            return
        session = db.get_session(Entity.Signal)
        signals = []
        if self.__code is not None:
            sgs = self.search_signal(fetch_data(self.__code, self.__klt, self.__begin))
            if len(sgs) > 0:
                for sgn in sgs:
                    sgn.code = self.__code
                    sgn.klt = self.__klt
                    signals.append(sgn)
        else:
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
