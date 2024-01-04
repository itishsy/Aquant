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
class HOT(Engine):

    def do_search(self):
        pass

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
