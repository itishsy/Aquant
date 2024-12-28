from engines.engine import Watcher, job_engine
from candles.finance import fetch_data
from candles.marker import mark
from signals.divergence import diver_top, diver_bottom
from models.choice import Choice
from models.ticket import Ticket


@job_engine
class B5(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 5)
        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            sig = dbs[-1]
            cho = Choice.select().where(Choice.code == code).first()
            Choice.select().where(Choice.code == code, Choice.freq == 30)
            if cho:
                if cho.freq == 30 and cho.dt < sig.dt:
                    if cho.price < sig.price:
                        return sig
                    else:
                        Choice.delete().where(Choice.code == code).execute()
            else:
                return sig


@job_engine
class B15(Watcher):

    def watch(self, code):
        candles = fetch_data(code, 15)
        candles = mark(candles)
        dbs = diver_bottom(candles)
        if len(dbs) > 0:
            sig = dbs[-1]
            cho = Choice.select().where(Choice.code == code).first()
            if cho:
                if cho.freq == 60 and cho.dt < sig.dt:
                    if cho.price < sig.price:
                        return sig
                    else:
                        Choice.delete().where(Choice.code == code).execute()
            else:
                return sig


@job_engine
class Tickets(Watcher):

    def watch(self, code):
        if Ticket.select().where(Ticket.code == code, Ticket.status == 1).exists():
            candles = fetch_data(code, 5)
            candles = mark(candles)
            dts = diver_top(candles)
            if len(dts) > 0:
                return dts[-1]
