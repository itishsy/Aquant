from abc import ABC, abstractmethod
from models.choice import Choice
from models.symbol import Symbol
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
        count = 0
        symbols = Symbol.actives()
        for sym in symbols:
            try:
                count = count + 1
                co = sym.code
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), co, self.strategy, count))
                sig = self.search(co)
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

    @abstractmethod
    def search(self, code):
        pass


class BaseWatcher(ABC):

    def start(self):
        tis = Ticket.select().where(Ticket.status.in_([Ticket.Status.PENDING, Ticket.Status.TRADING]))
        for ti in tis:
            try:
                print('[{0}] {1} searching by strategy -- {2}  '.format(datetime.now(), ti.code, self.strategy))
                sig5 = self.watch(ti.code, 5)
                if sig5:
                    sig5.code = ti.code
                    sig5.upset()
                sig15 = self.watch(ti.code, 15)
                if sig15:
                    sig15.code = ti.code
                    sig15.upset()

            except Exception as e:
                print(e)
        print('[{0}] search {1} done!  '.format(datetime.now(), self.strategy))

    @abstractmethod
    def watch(self, code, freq):
        pass
