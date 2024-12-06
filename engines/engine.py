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
                print('[{0}] {1} searching by {2} ({3}) '.format(datetime.now(), co, self.strategy, count))
                sig = self.search(co)
                if sig:
                    sig.code = co
                    sig.strategy = self.strategy
                    sig.stage = 'choice'
                    sig.upset()
                    if not Choice.select().where((Choice.code == co) & (Choice.strategy == self.strategy)).exists():
                        cho = Choice.create(code=co, name=sym.name, strategy=self.strategy, status=1, created=datetime.now(), updated=datetime.now())
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
        tis = Ticket.select().where(Ticket.status.in_([Ticket.Status.PENDING, Ticket.Status.TRADING]))
        for ti in tis:
            try:
                print('[{0}] {1} watch ticket -- {2}  '.format(datetime.now(), ti.code, self.strategy))
                sig = self.watch(ti.code)
                if sig:
                    sig.code = ti.code
                    sig.strategy = self.strategy
                    sig.stage = ti.id
                    sig.upset()
            except Exception as e:
                print(e)
        chs = Choice.select().where(Choice.strategy == 'u10')
        for ch in chs:
            try:
                print('[{0}] {1} watch u10 -- {2}  '.format(datetime.now(), ch.code, self.strategy))
                sig = self.watch(ch.code)
                if sig:
                    sig.code = ch.code
                    sig.strategy = self.strategy
                    sig.stage = ch.id
                    sig.upset()
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
