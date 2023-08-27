from engines.engine import strategy_engine, Engine
from storage.dba import get_symbol, find_candles
from models.signal import Signal
from signals.divergence import diver_bottom
from signals.utils import get_section, get_lowest
from common.utils import dt_format


@strategy_engine
class PAB(Engine):
    def search(self, code) -> Signal:
        candles = find_candles(code)
        size = len(candles)
        if size < 50:
            return

        # 不能超过618落在0轴下方
        counter = 0
        i = 0
        while i < size:
            if candles[i].diff() < 0:
                counter = counter + 1
            i = i + 1
        if counter / size > 0.618:
            return

        # 最近的30根出现过大涨
        j = len(candles) - 30
        counter = 0
        while j < len(candles):
            if (candles[j].close - candles[j - 1].close) / candles[j - 1].close > 0.095:
                counter = counter + 1
            j = j + 1
        if counter < 1:
            return

        # 发生30分钟低背离
        fc30 = find_candles(code, 30)
        s30 = diver_bottom(fc30)
        if len(s30) < 1:
            return
        sig = s30[-1]

        # 没有保存过
        if Signal.select().where(Signal.code == code, Signal.dt >= sig.dt).exists():
            return

        # 低背离的最低价不能破
        dt = dt_format(sig.dt)
        sec = get_section(candles, dt)
        if get_lowest(sec).low < sig.price:
            return

        sig.code = code
        sig.name = get_symbol(code).name
        sig.save()
        return sig

    def watch(self) -> Signal:
        pass

    def flush(self):
        pass

    def deal(self) -> Signal:
        pass

    def hold(self) -> Signal:
        pass
