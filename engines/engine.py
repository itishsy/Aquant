from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket
from models.signal import Signal
from common.dicts import TICKET_ENGINE
from storage.dba import find_candles
from signals.bs_signal import find_b_signal, find_s_signal
from signals.utils import *
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
        b_signal = find_b_signal(self.ticket.code, freq)
        if b_signal:
            sis = Signal.select().where(Signal.code == self.ticket.code, Signal.stage == 0).order_by(
                Signal.dt.desc()).limit(1)
            if len(sis) > 0:
                si = sis[-1]
                if b_signal.dt == si.dt and b_signal.freq == freq:
                    # 信号已保存过，检查有效性，更新有效性
                    if si.status == 0:
                        candles = find_candles(self.ticket.code, freq)
                        # 获取信号发出后一段的顶部
                        top = get_next_top(candles, b_signal.dt)
                        can = candles[-1]
                        if top:
                            # 顶部突破0轴，认为是有效的
                            if top.diff() > 0:
                                si.effect = 1
                                si.status = 1
                            else:
                                si.effect = 0
                                si.status = 1
                        else:
                            # 反弹未见顶，拿最后一根来判断
                            if can.diff() > 0:
                                si.effect = 1
                                si.status = 1



                elif b_signal.dt > si.dt:
                    # 保存新信号
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
