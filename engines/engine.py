from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from storage.dba import find_active_symbols, find_candles, get_symbol
from models.ticket import Ticket
from models.signal import Signal
from common.dicts import TICKET_ENGINE
import traceback

factory = {}


def register_engine(cls):
    cls_name = cls.__name__

    def register(clz):
        factory[cls_name] = clz

    return register(cls)


class Engine(ABC):
    ticket = None

    def start(self):
        bss = Ticket.select().where(Ticket.status != TICKET_ENGINE.KICK)
        for tick in bss:
            self.ticket = tick
            try:
                status = tick.status
                self.goto_watch()
                self.goto_deal()
                self.goto_wait()
                self.goto_kick()
                if status != self.ticket.status:
                    self.ticket.updated = datetime.now()
                    self.ticket.save()
            except Exception as e:
                traceback.print_exc()
            finally:
                ticket = None

    def goto_watch(self):
        if self.ticket.status == TICKET_ENGINE.WAIT:
            signal = self.find_buy_signal()
            if signal is not None:
                self.ticket.status = TICKET_ENGINE.WATCH

    def goto_wait(self):
        if self.ticket.status == TICKET_ENGINE.WATCH:
            signal = self.find_sell_signal()
            if signal is not None:
                self.ticket.status = TICKET_ENGINE.WAIT
        elif self.ticket.status == TICKET_ENGINE.DEAL:
            signal = self.find_sell_point()
            if signal is not None:
                self.ticket.status = TICKET_ENGINE.WAIT

    def goto_deal(self):
        if self.ticket.status == TICKET_ENGINE.WATCH:
            signal = self.find_buy_point()
            if signal is not None:
                self.ticket.status = TICKET_ENGINE.DEAL

    def goto_kick(self):
        if self.ticket.status == TICKET_ENGINE.WAIT:
            if self.is_kick():
                self.ticket.status = TICKET_ENGINE.KICK

    @abstractmethod
    def get_freq(self):
        pass

    @abstractmethod
    def get_strategy(self):
        pass

    @abstractmethod
    def find_buy_signal(self) -> Signal:
        pass

    @abstractmethod
    def find_sell_signal(self) -> Signal:
        pass

    @abstractmethod
    def find_buy_point(self) -> Signal:
        pass

    @abstractmethod
    def find_sell_point(self) -> Signal:
        pass

    @abstractmethod
    def is_kick(self) -> bool:
        return False
