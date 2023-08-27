from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket
from models.signal import Signal
from signals.utils import *
from common.utils import *
from common.dicts import TICKET_ENGINE
from models.component import Component
from storage.candle import Candle
from storage.fetcher import fetch_all
from storage.dba import find_active_symbols, find_candles, get_symbol

import traceback
import time

strategy = {}


def strategy_engine(cls):
    cls_name = cls.__name__

    def register(clz):
        strategy[cls_name] = clz

    return register(cls)


class Engine(ABC):
    ticket = None

    def start(self):
        while True:
            if is_trade_time():
                bss = Ticket.select().where(Ticket.status != TICKET_ENGINE.ZERO, Ticket.status != TICKET_ENGINE.KICK)
                for tick in bss:
                    self.ticket = tick
                    if tick.status == TICKET_ENGINE.WATCH:
                        sig = self.watch()
                    elif tick.status == TICKET_ENGINE.DEAL:
                        self.deal()
                    elif tick.status == TICKET_ENGINE.HOLD:
                        self.hold()
                    self.flush()
                    self.ticket = None
                time.sleep(60 * 10)
            else:
                if is_need_fetch():
                    fetch_all()
                if is_need_search(self.__class__.__name__):
                    self.search_new_ticket()
                time.sleep(60 * 30)
            if not is_trade_day():
                time.sleep(60 * 60 * 4)

    def search_new_ticket(self):
        symbols = find_active_symbols()
        count = 0
        for sym in symbols:
            count = count + 1
            print('[{0}] start searching... {1}({2}) '.format(datetime.now(), sym.code, count))
            sig = self.search(sym.code)
            if sig:
                add_ticket(sig, self.__class__.__name__)
        if count > 0:
            print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.__class__.__name__, count))

    @abstractmethod
    def search(self, code) -> Signal:
        pass

    @abstractmethod
    def watch(self) -> Signal:
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def deal(self) -> Signal:
        pass

    @abstractmethod
    def hold(self) -> Signal:
        pass


def is_need_fetch():
    fet = Component.get(Component.name == 'fetcher')
    ltm = fet.run_end
    now = datetime.now()
    if now.weekday() < 5:
        if now.hour > 15 and (ltm.month < now.month or ltm.day < now.day or ltm.hour < 16):
            return True
    elif ltm.weekday() < 4:
        return True
    return False


def is_need_search(s):
    if is_need_fetch():
        return False
    else:
        now = datetime.now()
        sea = Component.get(Component.name == 'search:{0}'.format(s))
        if sea.run_end.month < now.month or sea.run_end.day < now.day:
            return True
    return False


def add_ticket(sig: Signal, name):
    if Ticket.select().where(Ticket.code == sig.code).exists():
        ti = Ticket.get(Ticket.code == sig.code)
        ti.updated = datetime.now()
    else:
        ti = Ticket()
        ti.created = datetime.now()
    ti.code = sig.code
    ti.name = sig.name
    ti.strategy = name
    ti.cut = sig.price
    ti.status = TICKET_ENGINE.ZERO
    ti.source = 'strategy engine'
    ti.save()
    print('[{0}] add a ticket({1}) by strategy {2}'.format(datetime.now(), sig.code, name))

