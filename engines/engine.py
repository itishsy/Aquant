from abc import ABC, abstractmethod
from models.choice import Choice
from models.symbol import Symbol
from models.signal import Signal
from models.ticket import Ticket
from common.utils import *


engines = {}


def job_engine(cls):
    cls_name = cls.__name__.lower()[0] + cls.__name__[1:]

    def register(clz):
        engines[cls_name] = clz

    return register(cls)


class Searcher(ABC):
    strategy = 'searcher'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        count = 0
        symbols = Symbol.actives()
        Choice.delete().where(Choice.strategy == self.strategy).execute()
        for sym in symbols:
            try:
                count = count + 1
                co = sym.code
                sym.is_watch = 0
                sym.save()
                print('[{0}] {1} searching by {2} ({3}) '.format(datetime.now(), co, self.strategy, count))
                sig = self.search(co)
                if sig:
                    sig.code = co
                    sig.strategy = self.strategy
                    sig.stage = 'choice'
                    sig.upset()
                    if not Choice.select().where((Choice.code == co) & (Choice.strategy == self.strategy)).exists():
                        cho = Choice.create(code=co, name=sym.name, strategy=self.strategy, dt=sig.dt, price=sig.price, status=1, created=datetime.now(), updated=datetime.now())
                        Signal.update(oid=cho.id).where((Signal.code == co) & (Signal.strategy == self.strategy)).execute()
            except Exception as e:
                print(e)
        print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.strategy, count))

    @abstractmethod
    def search(self, code):
        pass


class Watcher(ABC):
    strategy = 'watcher'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        sis = []
        if self.strategy.startswith('s'):
            tis = Ticket.select().where(Ticket.status.in_([Ticket.Status.PENDING, Ticket.Status.TRADING]))
            for ti in tis:
                sig = self.watch(ti.code)
                if sig:
                    sig.code = ti.code
                    sig.name = ti.name
                    sis.append(sig)
        else:
            chs = Choice.select().where(Choice.strategy.in_(['u20', 'u60']))
            for ch in chs:
                print('[{0}] {1} watch choice -- {2}  '.format(datetime.now(), ch.code, ch.strategy))
                sig = self.watch(ch.code)
                if sig and sig.dt > ch.dt:
                    sig.code = ch.code
                    sig.strategy = ch.strategy
                    sig.name = ch.name
                    sis.append(sig)
            sls = Symbol.select().where(Symbol.is_watch == 1)
            for sl in sls:
                print('[{0}] {1} watch symbol u10 '.format(datetime.now(), sl.code, ))
                sig = self.watch(sl.code)
                if sig:
                    sig.code = sl.code
                    sig.strategy = 'u10'
                    sig.name = sl.name
                    sis.append(sig)

        for si in sis:
            try:
                print('[{0}] {1} watch -- {2}  '.format(datetime.now(), si.code, self.strategy))
                if not Signal.select().where(Signal.code == si.code, Signal.dt == si.dt).exists():
                    si.code = si.code
                    si.stage = 'watch'
                    si.notify = 0
                    si.upset()
            except Exception as e:
                print(e)
        print('[{0}] search {1} done!  '.format(datetime.now(), self.strategy))

    @abstractmethod
    def watch(self, code):
        pass


class Fetcher(ABC):
    strategy = 'fetcher'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        self.fetch()

    @abstractmethod
    def fetch(self):
        pass


class Sender(ABC):
    strategy = 'sender'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        self.send()

    @abstractmethod
    def send(self):
        pass
