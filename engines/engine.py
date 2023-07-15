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

    def save_signal(self, signal):
        signal.code = self.ticket.code
        signal.name = self.ticket.name
        signal.type = 0  # 买入
        signal.stage = 0  # 买入信号
        signal.status = signal.status if signal.status > 0 else 0  # 待确定
        signal.updated = datetime.now()
        signal.save()

    def do_wait(self):
        freq = self.get_freq()
        b_signal = find_b_signal(self.ticket.code, freq)
        if b_signal is not None:
            sis = Signal.select().where(Signal.code == self.ticket.code, Signal.stage == 0).order_by(
                Signal.dt.desc()).limit(1)
            # 获取上一个信号
            pre_signal = sis[-1] if len(sis) > 0 else None
            if pre_signal is None:
                # 上一个信号不存在，直接新建一个信号，状态为“待定”
                b_signal.created = datetime.now()
                self.save_signal(b_signal)
            elif pre_signal.type == 1:
                #  上一个是卖出信号，比买入信号的级别大，且买入信号处在卖出信号后的向下阶段，则认为是无效的
                if pre_signal.freq > b_signal.freq:
                    candles = find_candles(self.ticket.code, pre_signal.freq)
                    p_bottom = get_next_bottom(candles, pre_signal.dt)
                    if p_bottom.dt > b_signal.dt:
                        b_signal.effect = 0
                        b_signal.status = 1
                b_signal.created = datetime.now()
                self.save_signal(b_signal)
            else:
                if b_signal.dt == pre_signal.dt and b_signal.freq == freq:
                    # 如果信号已保存过，status未确认（0），则需要更新有效性
                    if pre_signal.status == 0:
                        # 信号发出后，检查向上反弹的一段，如果上穿突破0轴，则认为信号是有效的。
                        candles = find_candles(self.ticket.code, freq)
                        top = get_next_top(candles, b_signal.dt)
                        if top is not None:
                            if top.diff() > 0:
                                pre_signal.effect = 1
                                pre_signal.status = 1
                                self.save_signal(pre_signal)
                            else:
                                # 如果顶部拐点未突破0轴，且向下破前低，表示信号破坏
                                bottom = get_next_bottom(candles, top.dt)
                                lowest = get_lowest(get_stage(candles, bottom.dt))
                                if lowest.low < pre_signal.price:
                                    pre_signal.effect = 2  # 破坏
                                    pre_signal.status = 1
                                    self.save_signal(pre_signal)
                        else:
                            # 未出现顶部拐点，可能还处在上升期，拿最后一根来判断
                            can = candles[-1]
                            if can.diff() > 0:
                                last_b_signal.effect = 1
                                last_b_signal.status = 1
                                last_b_signal.updated = datetime.now()
                                last_b_signal.save()
                elif b_signal.dt > last_b_signal.dt:
                    candles = find_candles(self.ticket.code, freq)
                    # 跟最新存的信息比较。先取两者之间的candles
                    section = get_section(candles, si.dt, b_signal.dt)
                    # 保存新信号
                    self.ticket.strategy = self.get_strategy()
                    self.ticket.buy = freq
                    self.ticket.status = TICKET_ENGINE.WATCH
                    self.ticket.cut = b_signal.price
                    self.ticket.updated = datetime.now()
                    self.ticket.save()

    def do_watch(self):
        pass

    def do_deal(self):
        pass

    def do_kick(self):
        freq = self.get_freq()
        ss = find_s_signal(self.ticket.code, freq)
        if ss:
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
