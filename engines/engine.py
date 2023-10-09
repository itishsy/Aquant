from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket, TicketSignal, TICKET_STATUS
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
    strategy = 'engine'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        flag = False

        try:
            if self.need_to_start(COMPONENT_TYPE.WATCHER):
                flag = True
                self.do_watch()
            if self.need_to_start(COMPONENT_TYPE.FETCHER):
                flag = True
                fet.fetch_all()
            if self.need_to_start(COMPONENT_TYPE.SEARCHER):
                flag = True
                self.do_search()
        except Exception as e:
            print(e)
        finally:
            if flag:
                Component.update(status=Component.Status.READY, run_end=datetime.now()).where(
                    Component.status == Component.Status.RUNNING).execute()

    def need_to_start(self, comp_type):
        now = datetime.now()
        n_val = now.hour * 100 + now.minute
        flag = False

        comp = Component.get(Component.name == comp_type.format(self.strategy))
        if comp.status == Component.Status.READY:
            # 交易时间段，只启动watcher
            if now.weekday() < 5 and 930 < n_val < 1510:
                flag = comp_type == COMPONENT_TYPE.WATCHER
            else:
                # 当天没执行过，需要执行一次
                if comp.run_end.month < now.month or comp.run_end.day < now.day:
                    flag = True

                # 工作日当天已执行过，结束时间在16点前，也要执行一次
                if comp_type != COMPONENT_TYPE.WATCHER and comp.run_end.weekday() < 5 and comp.run_end.hour < 16:
                    flag = True

        if flag:
            comp.status = Component.Status.RUNNING
            comp.run_start = datetime.now()
            comp.save()

        return flag

    def do_search(self):
        count = 0
        symbols = find_active_symbols()
        for sym in symbols:
            try:
                count = count + 1
                cod = sym.code
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), cod,
                                                                             self.strategy, count))
                sig = self.search(cod)
                if sig:
                    Choice(source='ENGINE', strategy=self.strategy).add_by_signal(sig)
            except Exception as e:
                print(e)
        print('[{0}] search {1} done! ({2}) '.format(datetime.now(), self.strategy, count))

    def do_watch(self):
        chs = Choice.select().where(Choice.status == Choice.Status.WATCH)
        for cho in chs:
            try:
                print('[{0}] {1} watching by strategy -- {2} '.format(datetime.now(), cho.code, self.strategy))
                sig = self.watch(cho)
                if sig:
                    tic = Ticket()
                    tic.status = TICKET_STATUS.DEAL
                    tic.add_by_choice(cho, sig)
                    print('[{0}] add a ticket({1}) by strategy {2}'.format(datetime.now(), cho.code, self.strategy))
            except Exception as e:
                print(e)
            finally:
                print('[{0}] {1} watch done by strategy -- {2} '.format(datetime.now(), cho.code, self.strategy))

    def do_deal(self):
        tis = Ticket.select().where(Ticket.status == TICKET_STATUS.DEAL)
        for tic in tis:
            try:
                print('[{0}] {1} dealing by strategy -- {2} '.format(datetime.now(), tic.code, self.strategy))
                sig = self.deal(tic)
                if sig:
                    TicketSignal(tid=tic.id, sid=sig.id, created=datetime.now()).save()
            except Exception as e:
                print(e)
            finally:
                print('[{0}] {1} deal done by strategy -- {2} '.format(datetime.now(), tic.code, self.strategy))


    def upset_signal(self, sig: Signal):
        # 信号已经存在
        if Signal.select().where(Signal.code == sig.code, Signal.freq == sig.freq, Signal.dt == sig.dt).exists():
            si = Signal.get(Signal.code == sig.code, Signal.freq == sig.freq, Signal.dt == sig.dt)
            # 信号有效性已经验证，返回
            if si.effect:
                return

            lowest = get_lowest(find_candles(sig.code, begin=dt_format(sig.dt)))
            if lowest.low < sig.price:
                si.effect = SIGNAL_EFFECT.INVALID
                si.updated = datetime.now()
                si.save()
            elif sig.type == SIGNAL_TYPE.BOTTOM_DIVERGENCE:
                cds = find_candles(sig.code, freq=sig.freq)
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
            lowest = get_lowest(find_candles(sig.code, begin=dt_format(sig.dt)))
            # 信號价不能破
            if lowest.low < sig.price:
                return

            self.signal = sig
            self.signal.name = get_symbol(self.signal.code).name
            self.signal.created = datetime.now()
            self.signal.save()

    @abstractmethod
    def search(self, code) -> Signal:
        pass

    @abstractmethod
    def watch(self, cho: Choice) -> Signal:
        pass

    @abstractmethod
    def deal(self, tic: Ticket) -> Signal:
        pass
