from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket
from models.signal import Signal
from signals.utils import *
from common.utils import *
from common.dicts import TICKET_ENGINE
from models.component import Component
from storage.fetcher import fetch_all
import traceback
import time


factory = {}


def register_engine(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Engine(ABC):
    ticket = None

    def start(self):
        while True:
            if is_trade_day():
                if is_trade_time():
                    bss = Ticket.select().where(Ticket.status != TICKET_ENGINE.ZERO)
                    for tick in bss:
                        try:
                            self.ticket = tick
                            if tick.status == TICKET_ENGINE.WAIT:
                                self.do_watch()
                            elif tick.status == TICKET_ENGINE.DEAL or tick.status == TICKET_ENGINE.HOLD:
                                self.do_deal()
                            self.do_flush()
                        except Exception as e:
                            traceback.print_exc()
                        finally:
                            self.ticket = None
                elif is_need_fetch():
                    fetch_all()
                elif is_need_search():
                    self.do_search()
            else:
                time.sleep(60 * 60 * 4)

    @abstractmethod
    def do_search(self) -> List[Ticket]:
        pass

    @abstractmethod
    def do_watch(self) -> Signal:
        pass

    @abstractmethod
    def do_flush(self) -> Signal:
        pass

    @abstractmethod
    def do_deal(self) -> Signal:
        pass


def is_need_fetch(self):
    now = datetime.now()
    if now.weekday() < 5 and now.hour > 15:
        fet = Component.get(Component.name == 'fetcher')
        if fet.run_end.day < now.day or fet.run_end.hour < 15:
            return True
    return False


def is_need_search(self):
    now = datetime.now()
    if now.weekday() < 5 and now.hour > 15:
        fet = Component.get(Component.name == 'fetcher')
        if fet.run_end.day < now.day or fet.run_end.hour < 15:
            return False
        sea = Component.get(Component.name == 'searcher')
        if sea.run_end.day < now.day or sea.run_end.hour < 15:
            return True
    return False
