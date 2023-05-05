from storage.db import db, find_candles, find_active_symbols
from abc import ABC, abstractmethod
from entities.candle import Candle
from entities.signal import Signal
from entities.symbol import Symbol
from enums.entity import Entity
from typing import List


class Strategy(ABC):
    reverse = "反转",
    gold_cross = "零轴上方金叉",
    reverse_to_gold_cross = "（次级别）反转形成金叉",
    gold_cross_from_reverse = "反转后的金叉"

    def search_all(self):
        symbols = find_active_symbols()
        if len(symbols) == 0:
            return
        session = db.get_session(Entity.Signal)
        signals = []
        for sb in symbols:
            for klt in [102, 101, 60]:
                sgs = self.search_signal(find_candles(sb.code, klt, limit=100))
                if len(sgs) > 0:
                    for sgn in sgs:
                        sgn.code = sb.code
                        sgn.klt = klt
                        signals.append(sgn)
        if len(signals) > 0:
            session.add_all(signals)
            session.commit()

    @abstractmethod
    def search_signal(self, candles: List[Candle]) -> List[Signal]:
        pass


strategy_dict = {'reverse': '反转', 'gold_cross': '零轴上方金叉'}


class StrategyFactory:
    @staticmethod
    def search_all_signal():
        for key in strategy_dict.keys():
            strategy = eval(key)()
            strategy.search_all()
