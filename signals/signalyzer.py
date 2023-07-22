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
        effect = effect_analyse(si)
        if effect is not None:
            si.effect = effect
        strength = strength_analyse(si)
        if strength is not None:
            si.strength = strength


        pass


def effect_analyse(si: Signal):
    return None


def strength_analyse(si: Signal):
    pass
