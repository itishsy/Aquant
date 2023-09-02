import datetime

from engines.engine import strategy_engine, Engine
from storage.dba import get_symbol, find_candles
from models.signal import Signal
from models.ticket import Ticket
from signals.divergence import diver_bottom
from signals.utils import get_section, get_lowest
from common.utils import dt_format


@strategy_engine
class PAB(Engine):
    bs_freq = 30
    bp_freq = 5

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

        # 发生bs_freq底背离
        fcs = find_candles(code, self.bs_freq)
        dbs = diver_bottom(fcs)
        if len(dbs) > 0:
            self.add_signal(dbs[-1])

    def watch(self):
        fcs = find_candles(self.ticket.code, self.bp_freq)
        dbs = diver_bottom(fcs)
        if len(dbs) > 0:
            self.add_signal(dbs[-1])

    def flush(self):
        pass

    def deal(self) -> Signal:
        pass

    def hold(self) -> Signal:
        pass
