from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket, TICKET_STATUS
from models.choice import Choice
from models.signal import Signal, SIGNAL_TYPE, SIGNAL_STRENGTH, SIGNAL_EFFECT
from common.utils import *
from models.component import Component, COMPONENT_TYPE
import storage.fetcher as fet
from storage.dba import find_active_symbols, find_candles, get_symbol
from signals.utils import *

import traceback
import time

strategy = {}


def strategy_engine(cls):
    cls_name = cls.__name__

    def register(clz):
        strategy[cls_name] = clz

    return register(cls)


def is_need_watch(comp):
    # 交易时间开启
    if is_trade_day():
        return True

    # 当天没watch过，需要执行一次
    com = Component.get(Component.name == comp)
    if com.run_end.month < datetime.now().month or com.run_end.day < datetime.now().day:
        return True

    return False


def is_need_start(comp):
    sea = Component.get(Component.name == comp)
    if is_trade_day() and now_val() < 1600:
        # 交易时间不搜索
        return False
    if sea.run_end.month < datetime.now().month or sea.run_end.day < datetime.now().day:
        # 当天没搜索过，需要搜索
        return True
    elif sea.run_end.day == datetime.now().day:
        # 当天已搜索过，搜索结束时间是在工作日的16点前，仍要搜索
        return sea.run_end.weekday() < 5 and sea.run_end.hour < 16
    return False


class Engine(ABC):
    ticket = None
    signal = None

    def start(self):
        strategy_name = self.__class__.__name__.lower()
        if is_need_watch(COMPONENT_TYPE.WATCHER.format(strategy_name)):
            Component.update(status=1, run_start=datetime.now()).where(
                Component.name == COMPONENT_TYPE.WATCHER.format(strategy_name)).execute()
            bss = Ticket.select().where(Ticket.status != TICKET_STATUS.ZERO, Ticket.status != TICKET_STATUS.KICK)
            for tick in bss:
                self.ticket = tick
                self.do_watch()
                self.ticket = None
                self.signal = None
            Component.update(status=0, run_end=datetime.now()).where(
                Component.name == COMPONENT_TYPE.WATCHER.format(strategy_name)).execute()
        else:
            if is_need_start(COMPONENT_TYPE.FETCHER):
                Component.update(status=1, run_start=datetime.now()).where(
                    Component.name == COMPONENT_TYPE.FETCHER).execute()
                fet.fetch_all()
                Component.update(status=0, run_end=datetime.now()).where(
                    Component.name == COMPONENT_TYPE.FETCHER).execute()
            if is_need_start(COMPONENT_TYPE.SEARCHER.format(strategy_name)):
                Component.update(status=1, run_start=datetime.now()).where(
                    Component.name == COMPONENT_TYPE.SEARCHER.format(strategy_name)).execute()
                self.search_all()
                Component.update(status=0, run_end=datetime.now()).where(
                    Component.name == COMPONENT_TYPE.SEARCHER.format(strategy_name)).execute()

    def search_all(self):
        count = 0
        try:
            symbols = find_active_symbols()
            for sym in symbols:
                count = count + 1
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), sym.code,
                                                                             self.__class__.__name__.lower(), count))
                self.ticket = Ticket(code=sym.code, name=sym.name)
                self.search(sym.code)
                if self.signal:
                    self.add_choice()
                self.signal = None
                self.ticket = None
        except Exception as e:
            print(e)
        finally:
            self.signal = None
            self.ticket = None
            print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.__class__.__name__, count))

    def do_watch(self):
        try:
            if self.ticket.status == TICKET_STATUS.WATCH or self.ticket.status == TICKET_STATUS.DEAL:
                print('[{0}] {1} watching by strategy -- {2} '.format(datetime.now(), self.ticket.code,
                                                                      self.__class__.__name__.lower()))
                self.flush()
                if self.ticket.status == TICKET_STATUS.KICK:
                    Ticket.delete_by_id(self.ticket.get_id())
                if self.ticket.status == TICKET_STATUS.WATCH:
                    self.watch()
                    if self.signal:
                        self.ticket.status = TICKET_STATUS.DEAL
                        self.ticket.update_bp(self.signal)
            elif self.ticket.status == TICKET_STATUS.HOLD:
                self.hold()
        except Exception as e:
            print(e)

    def add_choice(self):
        if not Choice.select().where(Choice.code == self.signal.code,
                                     Choice.s_dt == self.signal.dt,
                                     Choice.s_freq == self.signal.freq).exists():
            cho = Choice()
            cho.source = 'ENGINE'
            cho.strategy = self.__class__.__name__
            cho.add_by_signal(sig=self.signal)
            print('[{0}] add a choice({1}) by strategy {2}'.format(datetime.now(),
                                                                   self.signal.code,
                                                                   self.__class__.__name__))

    def add_signal(self, sig: Signal):
        # 信号已经存在
        if Signal.select().where(Signal.code == sig.code, Signal.freq == sig.freq, Signal.dt == sig.dt).exists():
            si = Signal.get(Signal.code == sig.code, Signal.freq == sig.freq, Signal.dt == sig.dt)
            # 信号有效性已经验证，返回
            if si.effect:
                return

            lowest = get_lowest(find_candles(self.ticket.code, begin=dt_format(sig.dt)))
            if lowest.low < sig.price:
                si.effect = SIGNAL_EFFECT.INVALID
                si.updated = datetime.now()
                si.save()
            elif sig.type == SIGNAL_TYPE.BOTTOM_DIVERGENCE:
                cds = find_candles(self.ticket.code, freq=sig.freq)
                d, a, b, r, c = get_dabrc(cds, sig.dt)
                r_high = get_highest(r)
                if r_high.diff() > 0:
                    si.effect = SIGNAL_EFFECT.EFFECTIVE
                    si.strength = SIGNAL_STRENGTH.STRONG
                    si.save()
                else:
                    a_high = get_highest(a)
                    a_low = get_lowest(a)
                    if r_high.high > a_high.high:
                        si.effect = SIGNAL_EFFECT.EFFECTIVE
                        si.strength = SIGNAL_STRENGTH.STRONG
                        si.save()
                    elif r_high.high > (a_high.high + a_low.low) / 2:
                        si.strength = SIGNAL_STRENGTH.AVERAGE
                        si.save()
        else:
            lowest = get_lowest(find_candles(self.ticket.code, begin=dt_format(sig.dt)))
            # 信號价不能破
            if lowest.low < sig.price:
                return

            self.signal = sig
            self.signal.code = self.ticket.code
            self.signal.name = self.ticket.name
            self.signal.created = datetime.now()
            self.signal.save()

    @abstractmethod
    def search(self, code):
        pass

    @abstractmethod
    def watch(self):
        pass

    @abstractmethod
    def flush(self):
        pass

    @abstractmethod
    def hold(self):
        pass
