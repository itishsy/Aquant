from poker.card import two_card_str
from poker.config import BB
from decimal import Decimal
from poker.game import Stage


def fetch_by_level(cd, le):
    if len(cd.code) == le:
        return cd
    else:
        for c in reversed(cd.children):
            return fetch_by_level(c, le)


class Cond:
    code = '0'
    exp = ''
    children = []

    def __init__(self, exp):
        self.exp = exp

    def append_child(self, exp, level):
        parent = fetch_by_level(self, level)
        if parent:
            cd = Cond(exp)
            cd.code = '{}{}'.format(parent.code, len(parent.children) + 1)
            cd.children = []
            parent.children.append(cd)


class Strategy:

    GG003 = 'strategies/gg003.txt'

    def __init__(self, strategy_file):
        self.args = {}
        with open(strategy_file, 'r', encoding='utf-8') as file:
            line = file.readline()
            self.cond = Cond(line)
            while line:
                line = file.readline()
                self.cond.append_child(line.replace('\t', ''), line.count('\t'))

    def predict(self, game):
        self.args = {
            'stage': game.stage,
            'hand': two_card_str(game.card1, game.card2),
            'pool': int(game.sections[-1].pool/Decimal(str(BB))),
            'seat': game.seat
        }
        act = self.eval_act(self.cond)
        if 'fold' == act and game.card1[1] == game.card2[1]:
            self.args['hand'] = self.args['hand'] + 's'
            act = self.eval_act(self.cond)
        game.action = act

    def eval_act(self, co):
        for c in co.children:
            if not c.children:
                return c.exp
            if eval(c.exp, self.args):
                return self.eval_act(c)

