from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from storage.dba import find_active_symbols,find_candles, get_symbol
from models.signal import Signal
from models.ticket import Ticket
import traceback

factory = {}


def register_strategy(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Strategy(ABC):
    signals = []
    trades = []
    code = None
    begin = None
    freq = 101
    limit = 100

    def search_all(self):
        try:
            codes = []
            if self.code is None:
                symbols = find_active_symbols()
                for sym in symbols:
                    codes.append(sym.code)

            i = 1
            for code in codes:
                print('[{}] [{}] [{}] searching... {}'.format(datetime.now(), code, self.__class__.__name__, i))

                self.code = code
                candles = find_candles(code, self.freq, begin=self.begin, limit=self.limit)
                if len(candles) < self.limit:
                    continue

                ldt = candles[-1].dt
                if ldt.find(':') > 0:
                    sdt = datetime.strptime(ldt, '%Y-%m-%d %H:%M')
                else:
                    sdt = datetime.strptime(ldt, '%Y-%m-%d')
                if (sdt + timedelta(5)) < datetime.now():
                    continue

                self.search(candles)
                if len(self.signals) > 0:
                    self.upset_signals()
                    print('[{}] [{}] signals: {}'.format(datetime.now(), self.__class__.__name__, len(self.signals)))
                i = i + 1
        except Exception as e:
            traceback.print_exc()
        finally:
            self.code = None
            self.signals.clear()

    def deal_all(self):
        try:
            tickets = Ticket.select().where(Ticket.status < 2)
            for tick in tickets:
                self.deal(tick)
                if len(self.trades) > 0:
                    self.upset_trades()
        except Exception as e:
            traceback.print_exc()

    def upset_signals(self):
        if len(self.signals) > 0:
            for signal in self.signals:
                try:
                    if Signal.select().where(Signal.code == signal.code,Signal.freq == signal.freq).exists():
                        si = Signal.get(Signal.code == signal.code, Signal.freq == signal.freq)
                        si.status = 1
                        si.updated = datetime.now()
                        si.save()
                    else:
                        signal.tick = False
                        signal.name = get_symbol(signal.code).name
                        signal.status = 1
                        signal.created = datetime.now()
                        signal.updated = datetime.now()
                        signal.save()
                except Exception as e:
                    traceback.print_exc()

    def upset_trades(self):
        pass


    def child_freq(self, freq=None):
        if freq is None:
            freq = self.freq
        if freq == 101:
            return [60, 30]
        elif freq == 102:
            return [101]
        elif freq == 60:
            return [15]
        elif freq == 30:
            return [5]
        else:
            return [1]

    def grandchild_freq(self, freq=None):
        ks = self.child_freq(freq)
        cck = []
        for k in ks:
            cks = self.child_freq(k)
            for ck in cks:
                if ck not in cck:
                    cck.append(ck)
        return cck

    def parent_freq(self, freq=None):
        if freq is None:
            freq = self.freq
        if freq == 101:
            return 102
        elif freq in [30, 60]:
            return 101
        elif freq == 15:
            return 60
        elif freq == 5:
            return 30
        else:
            return 5

    @abstractmethod
    def search(self, candles):
        pass

    @abstractmethod
    def deal(self, tick):
        pass
