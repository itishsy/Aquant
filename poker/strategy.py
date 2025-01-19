from poker.game import Game, Action, Stage
from poker.card import Cards


class Strategy003:

    def __init__(self, game):
        self.pre_flop_allin_cards = ['AA']
        self.pre_flop_raise_cards = ['AK', 'KK', 'QQ']
        self.pre_flop_call_cards = ['AQ', 'AJ', 'AT', 'KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT', 'T9',
                                    'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22',
                                    'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 'Q9s', 'J9s', 'T9s']
        self.game = game

    def predict(self):
        if self.game.stage == 'PreFlop':
            self.game.action = self.pre_flop()
            if self.game.sections:
                self.game.sections[-1].action = self.game.action
        else:
            cards = Cards(self.game.card1, self.game.card2,
                          self.game.card3, self.game.card4, self.game.card5, self.game.card6, self.game.card7)
            card_power = cards.lookup()
            print(card_power, cards.to_string(card_power))

    def pre_flop(self):
        if self.game.card1 and self.game.card2:
            c1 = self.game.card1[0:1] + self.game.card2[0:1]
            c2 = self.game.card2[0:1] + self.game.card1[0:1]
            if c1 in self.pre_flop_allin_cards or c2 in self.pre_flop_allin_cards:
                return Action.AllIn
            if c1 in self.pre_flop_raise_cards or c2 in self.pre_flop_raise_cards:
                return Action.Raise
            if c1 in self.pre_flop_call_cards or c2 in self.pre_flop_call_cards:
                return Action.Call
            if (self.game.card1[1] == self.game.card2[1] and
                    (c1 + 's' in self.pre_flop_call_cards or c2 + 's' in self.pre_flop_call_cards)):
                return Action.Call
            return Action.Fold

    def flop(self):
        if self.game.stage == Stage.Flop:
            return Action.Null

    def turn(self):
        if self.game.stage == Stage.Turn:
            return Action.Null

    def river(self):
        if self.game.stage == Stage.River:
            return Action.Null


class Strategy03:

    def __init__(self, game):

        self.pre_flop_allin_cards = ['AA']
        self.pre_flop_raise_cards = ['AK', 'KK', 'QQ']
        self.pre_flop_call_cards = ['AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT', 'T9',
                                    'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
        self.pre_flop_call_card_suits = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                                         'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']

        self.game = game
