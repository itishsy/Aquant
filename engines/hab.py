from datetime import datetime
from engines.engine import strategy_engine, Engine
from storage.dba import get_symbol, find_candles
from models.signal import Signal
from models.choice import Choice
from models.ticket import Ticket
from signals.divergence import diver_bottom, diver_top
from signals.utils import *
from common.utils import dt_format
from models.hot import Hot


@strategy_engine
class HAB(Engine):

    def search(self, code):
        """ 热门个股
        #01. 10、20、60日线附近
        #02. 日线不能有顶背离。
        #03. 不可有效跌破60日线
        :param code:
        """
        if not Hot.select().where(Hot.code == code).exists():
            return

        # 不少于100根k线
        candles = find_candles(code)
        size = len(candles)
        if size < 100:
            return

        # REQ03
        dts = diver_top(candles)
        if len(dts) > 0 and dts[-1].dt > candles[50].dt:
            print('REQ03 return')
            return


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
