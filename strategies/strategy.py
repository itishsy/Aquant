from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from storage.dba import find_active_symbols,find_candles
from models.signal import Signal
import traceback

factory = {}


def register_strategy(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Strategy(ABC):
    signals = []
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

    def upset_signals(self):
        if len(self.signals) > 0:
            for signal in self.signals:
                try:
                    si = Signal.get(Signal.code == signal.code, Signal.freq == signal.freq)
                    si.status = 1
                    si.updated = datetime.now()
                    si.save()
                except:
                    signal.tick = False
                    signal.status = 1
                    signal.created = datetime.now()
                    signal.updated = datetime.now()
                    signal.save()

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
    def search(self, code):
        pass
