from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from models.ticket import Ticket, TicketSignal
from models.choice import Choice
from common.utils import *
from models.component import Component, COMPONENT_TYPE
import storage.fetcher as fet
from storage.dba import find_active_symbols

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
        flag = False

        try:
            if self.need_to_start(COMPONENT_TYPE.WATCHER):
                flag = True
                self.do_watch()
            if self.need_to_start(COMPONENT_TYPE.FETCHER):
                flag = True
                fet.fetch_all(clean=(datetime.now().weekday() == 5))
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
                co = sym.code
                print('[{0}] {1} searching by strategy -- {2} ({3}) '.format(datetime.now(), co,
                                                                             self.strategy, count))
                sig = self.search(co)
                if sig:
                    sig.code = co
                    sig.upset()
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

    @abstractmethod
    def search(self, code):
        pass

    @abstractmethod
    def watch(self, cho: Choice):
        pass

    @abstractmethod
    def deal(self, tic: Ticket):
        pass
