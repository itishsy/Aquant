from datetime import datetime, timedelta
from strategies.strategy import register_strategy, Strategy
from candles.storage import find_candles
from signals.divergence import diver_bottom, diver_top
from candles.candle import Candle
from models.choice import Choice
from models.symbol import Symbol
from typing import List
from signals.utils import get_stage, get_lowest


@register_strategy
class UAB15(Strategy):

    def search(self, candles: List[Candle]):
        size = len(candles)
        if size < 80:
            return

        cur = candles[-1]
        if cur.bar() > 0:
            return

        # 最近的20根站在ma20
        i = len(candles) - 20
        counter = 0
        while i < len(candles):
            if candles[i].ma20 is None:
                return
            if candles[i].close > candles[i].ma20:
                counter = counter + 1
            i = i + 1
        if counter < 18:
            return

        # 最近的50根出现过涨停
        j = len(candles) - 30
        counter = 0
        while len(candles) > j:
            if (candles[j].close - candles[j - 1].close) / candles[j - 1].close > 0.095:
                counter = counter + 1
            j = j + 1

        if counter < 1:
            return

        # 发生15分钟低背离
        fc15 = find_candles(self.code, 15)
        s15 = diver_bottom(fc15)
        if len(s15) > 0:
            # 15分钟回调中
            sig = s15[-1]
            low = get_lowest(get_stage(candles, cur.dt)).low
            if low < sig.price:
                return

            if not Choice.select().where(Choice.code == sig.code, Choice.freq == 15,
                                         Choice.dt == sig.dt).exists():
                cur_time = datetime.strptime(cur.dt, '%Y-%m-%d')
                sig_time = datetime.strptime(sig.dt, '%Y-%m-%d %H:%M')
                if sig_time + timedelta(5) > cur_time:
                    choice = Choice()
                    choice.code = self.code
                    choice.name = Symbol.get(Symbol.code == self.code).name
                    choice.freq = 15
                    choice.dt = sig.dt
                    choice.strategy = 'uab'
                    choice.value = sig.price
                    choice.status = 1
                    choice.created = datetime.now()
                    choice.save()
