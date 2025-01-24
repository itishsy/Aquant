from poker.game import Game, ActionType, Stage
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
        elif self.game.stage == 'Flop':
            self.game.action = self.flop()
            if self.game.sections:
                self.game.sections[-1].action = self.game.action
        elif self.game.stage == 'Turn':
            self.game.action = self.turn()
            if self.game.sections:
                self.game.sections[-1].action = self.game.action
        elif self.game.stage == 'River':
            self.game.action = self.turn()
            if self.game.sections:
                self.game.sections[-1].action = self.game.action

    def pre_flop(self):
        if self.game.card1 and self.game.card2:
            c1 = self.game.card1[0:1] + self.game.card2[0:1]
            c2 = self.game.card2[0:1] + self.game.card1[0:1]
            if c1 in self.pre_flop_allin_cards or c2 in self.pre_flop_allin_cards:
                return ActionType.AllIn
            if c1 in self.pre_flop_raise_cards or c2 in self.pre_flop_raise_cards:
                return ActionType.Raise
            if c1 in self.pre_flop_call_cards or c2 in self.pre_flop_call_cards:
                return ActionType.Call
            if (self.game.card1[1] == self.game.card2[1] and
                    (c1 + 's' in self.pre_flop_call_cards or c2 + 's' in self.pre_flop_call_cards)):
                return ActionType.Call
            return ActionType.Fold

    def flop(self):
        if self.game.stage == Stage.Flop:
            cards = Cards(self.game.card1, self.game.card2,
                          self.game.card3, self.game.card4, self.game.card5)
            card_power = cards.lookup()
            print('==>', cards.to_string(card_power))
            if card_power > Cards.Pair:
                return ActionType.Call
            else:
                return ActionType.Fold
        return ActionType.Null

    def turn(self):
        if self.game.stage == Stage.Turn:
            cards = Cards(self.game.card1, self.game.card2,
                          self.game.card3, self.game.card4, self.game.card5, self.game.card6)
            card_power = cards.lookup()
            print('==>', cards.to_string(card_power))
            if card_power > Cards.Two_Pair:
                return ActionType.Call
        return ActionType.Null

    def river(self):
        if self.game.stage == Stage.River:
            cards = Cards(self.game.card1, self.game.card2,
                          self.game.card3, self.game.card4, self.game.card5, self.game.card6, self.game.card7)
            card_power = cards.lookup()
            print('==>', cards.to_string(card_power))
            if card_power > Cards.Two_Pair:
                return ActionType.Call
        return ActionType.Null


class Strategy03:

    def __init__(self, game):

        self.pre_flop_allin_cards = ['AA']
        self.pre_flop_raise_cards = ['AK', 'KK', 'QQ']
        self.pre_flop_call_cards = ['AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT', 'T9',
                                    'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
        self.pre_flop_call_card_suits = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                                         'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']

        self.game = game
