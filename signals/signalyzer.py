from models.ticket import Ticket
from models.signal import Signal
from signals.utils import *

def analyse(code):
    if not Ticket.select().where(Ticket.code == code).exists():
        return

    if not Signal.select().where(Signal.code == code).exists():
        return

    ticket = Ticket.get(Ticket.code == code)
    sis = Signal.select().where(Signal.code == code).order_by(Signal.dt.desc()).limit(5)
    for si in sis:
        pass


def effect_analyse(si: Signal):
    pass


def strength_analyse(si: Signal):
    pass
