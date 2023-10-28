from datetime import datetime
from engines.engine import strategy_engine, Engine
from storage.dba import get_symbol, find_candles
from models.signal import Signal
from models.choice import Choice
from models.ticket import Ticket
from signals.divergence import diver_bottom, diver_top
from signals.utils import *
from common.utils import dt_format


@strategy_engine
class UAB(Engine):
    bs_freq = 30
    bp_freq = 5

    def search(self, code):
        """ 上涨趋势调整突破
        1. 前一次的上叉发生在0轴之上
        2. 价格调整的幅度不能超过上涨幅度的黄金分割线
        2. macd慢线调整不能超过0轴
        3. 调整过程中，出现次某级别的背驰买点
        :param code:
        """
        candles = find_candles(code)
        size = len(candles)
        if size < 50:
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

        # 最后一根在0轴上方，且macd向下调整
        tbs = get_top_bottom(candles)
        la1 = tbs[-1]
        if la1.mark < 0 and la1.diff() < 0:
            return

        # 倒数第二根在0轴上方
        la2 = tbs[-2]
        if la2.mark > 0 and la2.diff() > 0:
            return

        highest = get_highest(get_stage(candles, la1.dt))
        lowest1 = get_lowest(get_stage(candles, la2.dt))
        lowest2 = get_lowest(get_section(candles, la1.dt))

        # 价格调整的幅度判断
        if (highest.high - lowest2.low) / (highest.high - lowest1.low) > 0.618:
            return

        # 发生bs_freq底背离
        fcs = find_candles(code, self.bs_freq)
        dbs = diver_bottom(fcs)
        if len(dbs) > 0:
            sig = dbs[-1]
            lowest = get_lowest(get_section(fcs, sdt=sig.dt))
            # 剔除无效的信號
            if lowest.low >= sig.price:
                return sig

    def watch(self, cho):
        cho = self.choice
        lowest = get_lowest(find_candles(cho.code, begin=dt_format(cho.dt)))
        sig = Signal.get_by_id(cho.sid)
        if lowest.dt != sig.dt and lowest.low > sig.price:
            fcs = find_candles(cho.code, self.bp_freq)
            dbs = diver_bottom(fcs)
            if len(dbs) > 0:
                sig = dbs[-1]
                lowest = get_lowest(get_section(fcs, sdt=sig.dt))
                # 剔除无效的信號
                if lowest.low >= sig.price:
                    return sig
        else:
            self.choice.status = Choice.Status.KICK

    def deal(self, tic):
        dt = self.ticket.bs_dt
        lowest = get_lowest(find_candles(self.ticket.code, begin=dt_format(dt)))
        if lowest.low < self.ticket.bs_price:
            self.ticket.status = Ticket.Status.KICK
