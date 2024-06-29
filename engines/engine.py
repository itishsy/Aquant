from abc import ABC, abstractmethod
from models.choice import Choice
from models.symbol import Symbol
from models.signal import Signal
from common.utils import *
from models.component import Component, COMPONENT_TYPE
import candles.fetcher as fet
import candles.marker as mar
from signals.divergence import diver_bottom, diver_top
from candles.storage import find_candles


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
                    self.do_watch()
                if 1130 < n_val < 1300 or n_val > 1600:
                    self.start_search()
        except Exception as e:
            print(e)

    @staticmethod
    def start_fetch():
        freq = [101, 120, 60, 30]
        now = datetime.now()
        fetcher = Component.get(Component.name == 'fetcher')
        need_start = False
        if fetcher.status == Component.Status.READY:
            run_end_time = fetcher.run_end
            if run_end_time is None or not isinstance(run_end_time, datetime):
                need_start = True
            elif run_end_time.year != now.year or run_end_time.month != now.month or run_end_time.day != now.day:
                need_start = True
            elif now.weekday() < 5 and run_end_time.hour < 16 and now.hour > 16:
                freq = [30, 60]
                need_start = True
        if need_start:
            fetcher.status = Component.Status.RUNNING
            fetcher.run_start = datetime.now()
            fetcher.save()
            fet.fetch_all(freq=freq)
            fetcher.status = Component.Status.READY
            fetcher.run_end = datetime.now()
            fetcher.save()

    def start_search(self):
        now = datetime.now()
        eng = Component.get(Component.name == self.strategy)
        need_search = False
        if eng.status == Component.Status.READY:
            run_end_time = eng.run_end
            if run_end_time is None or not isinstance(run_end_time, datetime):
                need_search = True
            elif run_end_time.year != now.year or run_end_time.month != now.month or run_end_time.day != now.day:
                need_search = True
            elif now.weekday() < 5 and run_end_time.hour < 16 and now.hour > 16:
                need_search = True

        if not need_search:
            return

        eng.status = Component.Status.RUNNING
        eng.run_start = datetime.now()
        eng.save()
        self.do_search()
        eng.status = Component.Status.READY
        eng.run_end = datetime.now()
        eng.save()

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
            except Exception as e:
                print(e)
        print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.strategy, count))

    def do_watch(self):
        chs = Choice.select().where(Choice.status << [Choice.Status.WATCH, Choice.Status.DEAL],
                                    Choice.strategy ** '{}%'.format(self.strategy))
        for cho in chs:
            try:
                new_status = None
                if cho.status == Choice.Status.DEAL:
                    sig = self.find_sell_signal(cho)
                    print(
                        '[{0}] find {1} sell signal by {2} strategy, result:{3}'.format(datetime.now(), cho.code,
                                                                                        self.strategy,
                                                                                        (0 if sig is None else 1)))
                    if sig:
                        sig.stage = 'sell'
                        new_status = Choice.Status.DONE
                else:
                    sig = self.find_out_signal(cho)
                    print(
                        '[{0}] find {1} out signal by {2} strategy, result:{3}'.format(datetime.now(), cho.code,
                                                                                       self.strategy,
                                                                                       (0 if sig is None else 1)))
                    if sig:
                        sig.stage = 'out'
                        new_status = Choice.Status.DISUSE
                    else:
                        sig = self.find_buy_signal(cho)
                        print('[{0}] find {1} buy signal by {2} strategy, result:{3}'.format(datetime.now(), cho.code,
                                                                                             self.strategy,
                                                                                             (0 if sig is None else 1)))
                        if sig:
                            sig.stage = 'buy'
                            new_status = Choice.Status.DEAL
                if sig and not Signal.select().where(Signal.code == cho.code, Signal.freq == sig.freq,
                                                     Signal.dt == sig.dt).exists():
                    sig.code = cho.code
                    sig.name = Symbol.get(Symbol.code == cho.code).name
                    sig.strategy = self.strategy
                    sig.created = datetime.now()
                    sig.save()
                    if new_status == Choice.Status.DEAL:
                        cho.bid = sig.id
                    elif new_status == Choice.Status.DONE:
                        cho.sid = sig.id
                    else:
                        cho.oid = sig.id
                    cho.status = new_status
                    cho.updated = datetime.now()
                    cho.save()
                    print('[{0}] add a buy signal({1}) by strategy {2}'.format(datetime.now(), cho.code, self.strategy))
            except Exception as e:
                print('[{0}] {1} watch error -- {2} '.format(datetime.now(), cho.code, e))

    @staticmethod
    def fetch_candles(code, freq, begin=None):
        candles = fet.fetch_data(code, freq, begin)
        candles = mar.mark(candles=candles)
        return candles

    @staticmethod
    def common_filter(candles):
        candle_size = len(candles)
        if candle_size < 100:
            return

        t_size = 30
        turnover_size = 0
        for i in range(t_size):
            if candles[candle_size-i-1].turnover > 0.8:
                turnover_size = turnover_size + 1

        if turnover_size < 15:
            return False

        dts = diver_top(candles)
        if len(dts) > 0:
            return False

        return True

    def common_buy_point(self, c_sig, b_freq):
        if b_freq > 15:
            cds = find_candles(code=c_sig.code, freq=b_freq)
        else:
            cds = self.fetch_candles(code=c_sig.code, freq=b_freq)
        dbs = diver_bottom(cds)
        if dbs:
            b_sig = dbs[-1]
            if b_sig.dt > c_sig.dt and b_sig.price > c_sig.price:
                b_sig.type = 'diver-bottom'
                return b_sig

    @abstractmethod
    def find_choice_signal(self, code):
        pass

    @abstractmethod
    def find_buy_signal(self, cho: Choice):
        pass

    @abstractmethod
    def find_out_signal(self, cho: Choice):
        pass

    @abstractmethod
    def find_sell_signal(self, cho: Choice):
        pass
