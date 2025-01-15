from poker.game import Game, Action, Stage
from poker.card import Cards


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
        else:
            cards = Cards(self.game.card1, self.game.card2,
                          self.game.card3, self.game.card4, self.game.card5, self.game.card6, self.game.card7)
            card_power = cards.lookup()
            print(card_power, cards.to_string(card_power))

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
