from datetime import datetime
from engines.engine import strategy_engine, Engine
from storage.dba import get_symbol, find_candles
from models.signal import Signal
from models.choice import Choice, CHOICE_STATUS
from models.ticket import Ticket, TICKET_STATUS
from signals.divergence import diver_bottom, diver_top
from signals.utils import get_section, get_lowest
from common.utils import dt_format


@strategy_engine
class PAB(Engine):
    bs_freq = 30

    def get_bp_freq(self):
        if self.bs_freq == 101:
            return 30
        elif self.bs_freq == 60:
            return 10
        elif self.bs_freq == 30:
            return 5

    def search(self, code):
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

        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 发生bs_freq底背离
        fcs = find_candles(code, self.bs_freq)
        dbs = diver_bottom(fcs)
        if len(dbs) > 0:
            sig = dbs[-1]
            lowest = get_lowest(get_section(fcs, sdt=sig.dt))
            # 剔除无效的信號
            if lowest.dt == sig.dt or lowest.low > sig.price:
                sig.code = code
                self.upset_signal(sig)

    def watch(self):
        cho = self.choice
        lowest = get_lowest(find_candles(cho.code, begin=dt_format(cho.dt)))
        sig = Signal.get_by_id(cho.sid)
        if lowest.dt != sig.dt and lowest.low > sig.price:
            fcs = find_candles(cho.code, self.get_bp_freq())
            dbs = diver_bottom(fcs)
            if len(dbs) > 0:
                sig = dbs[-1]
                if sig.dt > cho.dt and sig.price > cho.price:
                    sig.code = cho.code
                    self.upset_signal(sig)
        else:
            self.choice.status = CHOICE_STATUS.REMOVE

    def deal(self):
        dt = self.ticket.bs_dt
        lowest = get_lowest(find_candles(self.ticket.code, begin=dt_format(dt)))
        if lowest.low < self.ticket.bs_price:
            self.ticket.status = TICKET_STATUS.KICK
