from config import *


class Action:

    def __init__(self):
        self.desktops = []

    def add(self, desktop):
        self.desktops.append(desktop)

    def clear(self):
        self.desktops.clear()

    def pre_flop(self):
        desktop = self.desktops[-1]
        if desktop and desktop.card1 and desktop.card2:
            c1 = desktop.card1[0:1] + desktop.card2[0:1]
            c2 = desktop.card2[0:1] + desktop.card1[0:1]
            if c1 in RAISE_CARDS or c2 in RAISE_CARDS:
                return ACT.Raise
            if c1 in CALL_CARDS or c2 in CALL_CARDS:
                return ACT.Call
            if c1 in CALL_CARD_SUITS or c2 in CALL_CARD_SUITS:
                if desktop.card1[1] == desktop.card2[1]:
                    return ACT.Check
        return ACT.Fold

    def flop(self):
        desktop = self.desktops[-1]
        return ACT.Check

    def turn(self):
        # desktop = self.desktops[-1]
        return ACT.Check

    def river(self):
        # desktop = self.desktops[-1]
        return ACT.Check
