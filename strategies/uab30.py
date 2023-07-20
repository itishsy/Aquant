from datetime import datetime, timedelta
from strategies.strategy import register_strategy, Strategy
from storage.dba import find_candles, get_symbol
from signals.divergence import diver_bottom, diver_top
from storage.candle import Candle
from models.choice import Choice
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

        # 最近的30根站在ma30
        i = len(candles) - 30
        counter = 0
        while i < len(candles):
            if candles[i].ma30 is None:
                return
            if candles[i].close > candles[i].ma30:
                counter = counter + 1
            i = i + 1
        if counter < 25:
            return

        # 最近的50根出现过涨停
        j = len(candles) - 50
        counter = 0
        while j < len(candles):
            if (candles[j].close - candles[j - 1].close) / candles[j - 1].close > 0.095:
                counter = counter + 1
            j = j + 1

        if counter < 2:
            return

        # 发生30分钟低背离
        fc30 = find_candles(self.code, 30)
        s30 = diver_bottom(fc30)
        if len(s30) > 0:
            # 30分钟回调中
            sig = s30[-1]
            low = get_lowest(get_stage(candles, cur.dt)).low
            if low < sig.price:
                return

            if not Choice.select().where(Choice.code == sig.code, Choice.freq == 30,
                                         Choice.dt == sig.dt).exists():
                cur_time = datetime.strptime(cur.dt, '%Y-%m-%d')
                sig_time = datetime.strptime(sig.dt, '%Y-%m-%d %H:%M')
                if sig_time + timedelta(8) > cur_time:
                    choice = Choice()
                    choice.code = self.code
                    choice.name = get_symbol(self.code).name
                    choice.freq = 30
                    choice.dt = sig.dt
                    choice.strategy = 'uab'
                    choice.value = sig.price
                    choice.status = 1
                    choice.created = datetime.now()
                    choice.save()
