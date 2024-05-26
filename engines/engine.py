from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket, TicketSignal
from models.choice import Choice
from models.symbol import Symbol
from common.utils import *
from common.config import Config
from models.component import Component, COMPONENT_TYPE
import candles.fetcher as fet
from signals.divergence import diver_top

import traceback
import time

strategy = {}


def strategy_engine(cls):
    cls_name = cls.__name__

    def register(clz):
        strategy[cls_name] = clz

    return register(cls)


class Engine(ABC):
    strategy = 'engine'

    def start(self):
        self.strategy = self.__class__.__name__.lower()
        now = datetime.now()
        n_val = now.hour * 100 + now.minute
        try:
            if now.weekday() < 5:
                if 1130 < n_val < 1300 or 1530 < n_val < 1700:
                    # 盘后检索
                    freq = [30, 60] if 1130 < n_val < 1300 else [101, 120, 60, 30]
                    limit_time = 1130 if 1130 < n_val < 1300 else 1530
                    self.start_component('fetcher', limit_time=limit_time, freq=freq)
                    self.start_component(self.strategy, limit_time=limit_time)
                elif 930 < n_val < 1130 or 1300 < n_val < 1500:
                    # 盘中观察
                    self.do_watch()
                else:
                    # 当天跑一次
                    self.start_component('fetcher')
                    self.start_component(self.strategy)
            else:
                # 当天跑一次
                self.start_component('fetcher')
                self.start_component(self.strategy)
        except Exception as e:
            print(e)

    def start_component(self, comp_name, limit_time=1, freq=Config.FREQ, clean=False):
        now = datetime.now()
        comp = Component.get(Component.name == comp_name)
        is_fetcher = comp_name == 'fetcher'
        flag = False
        if isinstance(comp.run_end, str) or isinstance(comp.run_start, str):
            flag = True
        else:
            run_end = comp.run_end.hour * 100 + comp.run_end.minute
            if comp.status == Component.Status.READY and (comp.run_end.day < now.day or run_end < limit_time):
                flag = True

        if flag:
            comp.status = Component.Status.RUNNING
            comp.run_start = datetime.now()
            comp.save()
            if is_fetcher:
                if now.weekday() < 5 or comp.run_end.day > (now.day - 2):
                    fet.fetch_all(freq, clean)
            else:
                self.do_search()
            comp.status = Component.Status.READY
            comp.run_end = datetime.now()
            comp.save()

    def do_search(self):
        count = 0
        symbols = Symbol.actives()
        for sym in symbols:
            try:
                count = count + 1
                co = sym.code
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), co,
                                                                             self.strategy, count))
                sig = self.search(co)
                if sig:
                    sig.code = co
                    sig.strategy = self.strategy
                    sig.upset()
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
                    sig.code = cho.code
                    sig.upset()
                    tic = Ticket()
                    tic.status = Ticket.Status.DEAL
                    tic.add_by_choice(cho, sig)
                    print('[{0}] add a ticket({1}) by strategy {2}'.format(datetime.now(), cho.code, self.strategy))
            except Exception as e:
                print(e)
            finally:
                print('[{0}] {1} watch done by strategy -- {2} '.format(datetime.now(), cho.code, self.strategy))

    def do_deal(self):
        tis = Ticket.select().where(Ticket.status == Ticket.Status.DEAL)
        for tic in tis:
            try:
                print('[{0}] {1} dealing by strategy -- {2} '.format(datetime.now(), tic.code, self.strategy))
                sig = self.deal(tic)
                if sig:
                    sig.code = tic.code
                    sig.upset()
                    TicketSignal(tid=tic.id, sid=sig.id, created=datetime.now()).save()
            except Exception as e:
                print(e)
            finally:
                print('[{0}] {1} deal done by strategy -- {2} '.format(datetime.now(), tic.code, self.strategy))

    @staticmethod
    def common_filter(candles):
        candle_size = len(candles)
        if candle_size < 100:
            return

        turnover_size = 0
        for candle in candles:
            if candle.turnover > 1:
                turnover_size = turnover_size + 1

        if turnover_size/candle_size < 0.6:
            return False

        dts = diver_top(candles)
        if len(dts) > 0:
            return False

        return True

    @abstractmethod
    def search(self, code):
        pass

    @abstractmethod
    def watch(self, cho: Choice):
        pass

    @abstractmethod
    def deal(self, tic: Ticket):
        pass
