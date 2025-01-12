from game import Game, Action, Stage


RAISE_CARDS = ['AA', 'KK']
CALL_CARDS = ['AK', 'AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT', 'T9',
              'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
CALL_CARD_SUITS = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                   'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']


class Strategy:

    def __init__(self, game):
        self.game = game

    def predict(self):
        if self.game.stage == 'PreFlop':
            self.game.action = self.pre_flop()
            if self.game.sections:
                self.game.sections[-1].action = self.game.action

    def set_player_action(self, idx, act, tail=-1):
        sec = self.game.sections[tail]
        if sec:
            exec("sec.player{}_action = '{}'".format(idx, act))

    def analyze(self):
        six = len(self.game.sections)
        if six > 1:
            sec_1, sec_2 = self.game.sections[-1], self.game.sections[-2]
            pool_raised = sec_1.pool > sec_2.pool
            for i in range(1, 6):
                act_2 = eval('sec_2.player{}_action'.format(i))
                if act_2 == 'fold':
                    self.set_player_action(i, 'fold')
                    continue

                amt_1 = eval('sec_1.player{}_amount'.format(i))
                amt_2 = eval('sec_2.player{}_amount'.format(i))
                diff_amt = amt_2 - amt_1 if amt_1 and amt_2 else 0
                is_same_stage = sec_1.get_stage() == sec_2.get_stage()

                if pool_raised:
                    if diff_amt == 0:
                        # 底池增加，玩家金额不变，说明位置在前为fold，位置在后为pending
                        if i < self.game.seat:
                            self.set_player_action(i, 'fold')
                        else:
                            self.set_player_action(i, 'pending')
                    else:
                        # 底池增加，玩家金额减少，说明位置在前为fold，位置在后为pending
                        self.set_player_action(i, 'bet:{}'.format(diff_amt))
                else:
                    # 底池不变
                    if act_2 == 'pending':
                        self.set_player_action(i, 'check', tail=-2)
                    if i < self.game.seat:
                        self.set_player_action(i, 'check')
                    else:
                        self.set_player_action(i, 'pending')

    def pre_flop(self):
        if self.game.card1 and self.game.card2:
            c1 = self.game.card1[0:1] + self.game.card2[0:1]
            c2 = self.game.card2[0:1] + self.game.card1[0:1]
            if c1 in RAISE_CARDS or c2 in RAISE_CARDS:
                return Action.Raise
            if c1 in CALL_CARDS or c2 in CALL_CARDS:
                return Action.Call
            if c1 in CALL_CARD_SUITS or c2 in CALL_CARD_SUITS:
                if self.game.card1[1] == self.game.card2[1]:
                    return Action.Check
            return Action.Check

    def flop(self):
        if self.game.stage == Stage.Flop:
            return []

    def turn(self):
        if self.game.stage == Stage.Turn:
            return []

    def river(self):
        if self.game.stage == Stage.River:
            return []
