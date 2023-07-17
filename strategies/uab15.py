import datetime

from strategies.strategy import register_strategy, Strategy
from storage.dba import find_candles
from signals.divergence import diver_bottom, diver_top
from storage.candle import Candle
from models.choice import Choice
from typing import List
from decimal import Decimal


@register_strategy
class UAB15(Strategy):


    def search(self, candles: List[Candle]):
        size = len(candles)
        if size < 80:
            return

        # 最近的30根站在ma30
        i = len(candles) - 30
        counter = 0
        while i < len(candles):
            if candles[i].ma30 is None:
                return
            if candles[i].close > candles[i].ma20:
                counter = counter + 1
            i = i + 1

        # 最近的50根出现过涨停
        j = len(candles) - 50
        flag = True
        while j < len(candles):
            if (candles[j].close - candles[j - 1].close) / candles[j - 1].close > 0.095:
                flag = False
                break
            j = j + 1
        if flag:
            return

        # 发生15分钟低背离
        xcs = find_candles(self.code, 15)
        dbs = diver_bottom(xcs)
        if len(dbs) == 0:
            return

        # 15分钟回调中
        cur = candles[-1]
        if cur.bar() > 0:
            return

        choice = Choice()
        choice.code = self.code
        choice.freq = 15
        choice.dt = dbs[-1].dt
        choice.strategy = 'uab'
        choice.value = dbs[-1].price
        choice.status = 1
        choice.created = datetime.datetime.now()
        choice.save()
