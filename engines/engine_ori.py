from abc import ABC, abstractmethod
from models.choice import Choice
from models.symbol import Symbol
from models.signal import Signal
from models.ticket import Ticket
from common.utils import *
from models.component import Component
import candles.finance as fet
import candles.marker as mar
from signals.divergence import diver_bottom, diver_top
from candles.storage import find_candles
import signals.utils as utl


strategy = {}


def strategy_engine(cls):
    cls_name = cls.__name__.lower()[0] + cls.__name__[1:]

    def register(clz):
        strategy[cls_name] = clz

    return register(cls)


class Engine(ABC):
    strategy = 'engine'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        now = datetime.now()
        try:
            self.start_fetch()
            if now.weekday() < 5:
                n_val = now.hour * 100 + now.minute
                if 930 < n_val < 1130 or 1300 < n_val < 1530:
                    self.start_watch()
                if 1130 < n_val < 1300 or n_val > 1600:
                    self.start_search()
        except Exception as e:
            print(e)

    @staticmethod
    def need_start(comp: Component):
        now = datetime.now()
        if comp.status == Component.Status.READY:
            run_end_time = comp.run_end
            if run_end_time is None or not isinstance(run_end_time, datetime):
                return True
            if run_end_time.year != now.year or run_end_time.month != now.month or run_end_time.day != now.day:
                return True
            if now.weekday() < 5 and run_end_time.hour < 16 and now.hour > 16:
                return True
        return False

    def start_fetch(self):
        freq = [101, 120, 60, 30]
        now = datetime.now()
        fetcher = Component.get(Component.name == 'fetcher')
        if self.need_start(fetcher):
            fetcher.status = Component.Status.RUNNING
            fetcher.run_start = datetime.now()
            fetcher.save()
            if now.weekday() == 5:
                freq = [102, 101, 120, 60, 30]
                Symbol.fetch()
                # fet.fetch_all(freq=freq, clean=True)
            else:
                pass
                # fet.fetch_all(freq=freq)
            fetcher.status = Component.Status.READY
            fetcher.run_end = datetime.now()
            fetcher.save()

    def start_search(self):
        eng = Component.get(Component.name == self.strategy)
        if self.need_start(eng):
            eng.status = Component.Status.RUNNING
            eng.run_start = datetime.now()
            eng.save()
            self.do_search()
            eng.status = Component.Status.READY
            eng.run_end = datetime.now()
            eng.save()

    def start_watch(self):
        tis = Ticket.select().where(Ticket.status.in_([Ticket.Status.PENDING, Ticket.Status.TRADING]))
        for ti in tis:
            if ti.status == Ticket.Status.PENDING:
                b_sig = Signal.select().where(Signal.id == ti.bid)
                bp = self.common_buy_point(b_sig)
                if bp:
                    bp.notify = 0
                    bp.save()
            else:
                self.do_watch(ti)

    def do_search(self):
        count = 0
        symbols = Symbol.actives()
        for sym in symbols:
            try:
                count = count + 1
                co = sym.code
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), co, self.strategy, count))
                sig = self.find_choice_signal(co)
                if sig:
                    sig.code = co
                    sig.strategy = self.strategy
                    sig.stage = 'choice'
                    sig.upset()
                    if not Choice.select().where(Choice.sid == sig.id).exists():
                        Choice.create(code=sig.code, name=sig.name, cid=sig.id, strategy=sig.strategy,
                                      created=datetime.now(), updated=datetime.now())
            except Exception as e:
                print(e)
        print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.strategy, count))

    def do_watch(self, ti: Ticket):
        try:
            sig = self.find_bs_point(ti)
            if sig:
                sig.code = ti.code
                sig.name = ti.name
                sig.notify = 0
                sig.strategy = self.strategy
                sig.created = datetime.now()
                sig.id = None
                sig.save()
                ti.sid = sig.id
                ti.status = Ticket.Status.SOLD
                ti.updated = datetime.now()
                ti.save()
                print('[{0}] {1} find a sell signal by {2} strategy'.format(datetime.now(), ti.code,
                                                                            self.strategy))
        except Exception as e:
            print('[{0}] {1} watch ticket error -- {2} '.format(datetime.now(), ti.code, e))

    @staticmethod
    def common_buy_point(b_sig):
        cds1 = find_candles(b_sig.code, freq=1)
        dbs = diver_bottom(cds1)
        if len(dbs) > 0:
            sig = dbs[-1]
            if sig.dt > b_sig.dt and sig.price > b_sig.price:
                return sig

        cds = find_candles(b_sig.code, freq=b_sig.freq)
        crs = utl.get_cross(cds)
        if len(crs) > 2 and crs[0] == 1 and crs[1].dt > b_sig.dt:
            st1 = utl.get_stage(crs[1])
            st2 = utl.get_stage(crs[2])
            if utl.get_lowest(st1).low > b_sig.price and utl.contains(st2, b_sig.dt):
                return Signal(code=b_sig.code, name=b_sig.name, freq=b_sig.freq, price=crs[0].low, dt=crs[0].dt,
                              type='cross-bp')

    @staticmethod
    def common_buy_signal(c_sig, b_freq):
        if b_freq > 15:
            cds = find_candles(code=c_sig.code, freq=b_freq)
        else:
            candles = fet.fetch_data(c_sig.code, b_freq)
            cds = mar.mark(candles=candles)
        dbs = diver_bottom(cds)
        if dbs:
            b_sig = dbs[-1]
            if b_sig.dt > c_sig.dt and b_sig.price > c_sig.price:
                b_sig.type = 'diver-bottom'
                return b_sig

    @staticmethod
    def common_sell_signal(c_sig: Signal, b_sig: Signal):
        # 次级别顶背离
        if int(b_sig.freq) > 15:
            cds = find_candles(code=c_sig.code, freq=b_sig.freq)
        else:
            candles = fet.fetch_data(c_sig.code, b_sig.freq)
            cds = mar.mark(candles=candles)
        dbs = diver_top(cds)
        if len(dbs) > 0:
            sig = dbs[-1]
            if b_sig.dt < sig.dt:
                sig.type = 'diver-top'
                return sig

        # 止损线
        for cd in cds:
            if cd.dt > b_sig.dt and cd.low < b_sig.price:
                return Signal(code=c_sig.code, name=c_sig.name, freq=c_sig.freq, price=cd.low, dt=cd.dt, type='damage-bs')

        # 长上影线
        cds1 = find_candles(code=c_sig.code, begin=c_sig.dt)
        highest = utl.get_highest(cds1)
        if utl.is_upper_shadow(highest) and highest.dt > b_sig.dt:
            return Signal(code=c_sig.code, name=c_sig.name, freq=c_sig.freq, dt=highest.dt, type='up-shadow')

        cds2 = find_candles(code=c_sig.code, freq=c_sig.freq, begin=c_sig.dt)
        cross = utl.get_cross(cds2)
        if cross[-1].mark == 1 and cross[-1].dt > b_sig.dt:
            return Signal(code=c_sig.code, name=c_sig.name, freq=c_sig.freq, dt=cross[-1].dt, type='cross-down')

    @staticmethod
    def common_out(c_sig, timeout=None):
        cds = find_candles(c_sig.code, begin=c_sig.dt)

        if timeout and len(cds) > timeout:
            sig = c_sig
            sig.id = None
            sig.dt = cds[-1].dt
            sig.type = 'timeout'
            return sig

        for cd in cds:
            if cd.low < c_sig.price:
                sig = c_sig
                sig.id = None
                sig.dt = cd.dt
                sig.type = 'damage'
                return sig

    @abstractmethod
    def find_choice_signal(self, code):
        pass

    @abstractmethod
    def find_bs_point(self, ti: Ticket):
        pass

