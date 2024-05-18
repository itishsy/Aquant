from datetime import datetime, timedelta
from engines.engine import strategy_engine, Engine
from candles.storage import find_stage_candles, find_candles
from models.signal import Signal
from models.choice import Choice
from models.ticket import Ticket
from signals.divergence import diver_bottom, diver_top
from signals.utils import get_section, get_lowest, get_highest, get_next_top
from common.utils import dt_format


@strategy_engine
class PAB(Engine):
    parent_freq = 102
    bs_freq = 101
    bp_freq = 30

    def search(self, code):
        """ 平台调整突破
        #01. 周线级别的快慢线向下交叉发生在0轴上方
        #02. 日线不能处在下跌趋势中。DIFF不能全在0轴下方。
        #03. 具有一定的活跃性，最近30交易日出现过大涨
        #04. 近期的日线，未发生过顶背底信号
        #05. 出现日线级别底背底信号
        :param code:
        """

        # 不少于100根k线
        candles = find_candles(code)
        size = len(candles)
        if size < 100:
            return

        # 父級別换手大于10
        p_cds = find_candles(code, self.parent_freq)
        p_size = len(p_cds)
        p_j = p_size - 10
        p_counter = 0
        while p_j < len(p_cds):
            if p_cds[p_j].turnover < 10:
                p_counter = p_counter + 1
            p_j = p_j + 1
        if p_counter / p_size > 0.6:
            return

        # 父級別的一段起點在0轴上方
        # psc = find_stage_candles(code, self.parent_freq, p_cds[-1])
        # if len(psc) < 2 or psc[0].diff() < 0:
        #     return

        # 父級別未发生顶背离
        pdt = diver_top(p_cds)
        if len(pdt) > 0:
            return

        #  日线diff不要超过618落在0轴下方
        counter = 0
        i = 0
        while i < size:
            if candles[i].diff() < 0:
                counter = counter + 1
            i = i + 1
        if counter / size > 0.8:
            return

        # 近期没有出现顶背离
        dts = diver_top(candles)
        if len(dts) > 0:
            return

        # 发生了日线底背离
        fcs = find_candles(code, self.bs_freq)
        dbs = diver_bottom(fcs)
        if len(dbs) > 0:
            sig = dbs[-1]
            lowest = get_lowest(get_section(fcs, sdt=sig.dt))
            # 信號发出后不可再创新低
            if lowest.low >= sig.price:
                top = get_next_top(candles, sig.dt)
                if top and top.diff() > 0:
                    return sig

    def watch(self, cho):
        cho_dt = datetime.strptime(cho.dt, '%Y-%m-%d')
        nex_dt = (cho_dt + timedelta(1)).strftime('%Y-%m-%d')
        nex_lowest = get_lowest(find_candles(cho.code, begin=nex_dt))
        if nex_lowest.low >= cho.price and cho_dt + timedelta(90) > datetime.now():
            fcs = find_candles(cho.code, self.bp_freq)
            dbs = diver_bottom(fcs)
            if len(dbs) > 0:
                sig = dbs[-1]
                if sig.dt > cho.dt and sig.price > cho.price:
                    sig.code = cho.code
                    cho.status = Choice.Status.DEAL
                    cho.updated = datetime.now()
                    cho.save()
                    return sig
        else:
            cho.status = Choice.Status.KICK
            cho.updated = datetime.now()
            cho.save()

    def deal(self, tic):
        lowest = get_lowest(find_candles(self.ticket.code, begin=dt_format(tic.dt)))
        if lowest.low < self.ticket.bs_price:
            tic.status = Ticket.Status.KICK
            tic.updated = datetime.now()
            tic.save()
        else:
            fcs = find_candles(tic.code, self.bp_freq)
            dbs = diver_top(fcs)
            if len(dbs) > 0:
                sig = dbs[-1]
                if sig.dt > tic.dt and sig.price > tic.price:
                    sig.code = tic.code
                    return sig
