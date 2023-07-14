from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket
from models.signal import Signal
from common.dicts import TICKET_ENGINE
from signals.bs_signal import find_b_signal, find_s_signal
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
            try:
                self.ticket = tick
                if tick.status == TICKET_ENGINE.WAIT:
                    self.do_wait()
                    self.do_kick()
                elif tick.status == TICKET_ENGINE.WATCH:
                    self.do_watch()
                elif tick.status == TICKET_ENGINE.DEAL or tick.status == TICKET_ENGINE.HOLD:
                    self.do_deal()
                self.ticket = None
            except Exception as e:
                traceback.print_exc()
            finally:
                self.ticket = None

    def do_wait(self):
        freq = self.get_freq()
        bs = find_b_signal(self.ticket.code, freq)
        if bs:
            sis = Signal.select().where(Signal.code == self.ticket.code).order_by(
                Signal.dt.desc()).limit(1)
            if sis:
                si = sis[-1]
                if bs.dt > si.dt:
                    self.ticket.strategy = self.get_strategy()
                    self.ticket.buy = freq
                    self.ticket.status = TICKET_ENGINE.WATCH
                    self.ticket.cut = bs.price
                    self.ticket.updated = datetime.now()
                    self.ticket.save()
            else:
                bs.type = 0
                bs.code = self.ticket.code
                bs.name = self.ticket.name
                bs.created = datetime.now()
                bs.save()
        ss = find_s_signal(self.ticket.code, freq)
        if ss:
            self.ticket.status = TICKET_ENGINE.KICK

    def do_watch(self):
        pass

    def do_deal(self):
        pass

    def do_kick(self):
        pass

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
