from entities import Game, Action


RAISE_CARDS = ['AA', 'KK']
CALL_CARDS = ['AK', 'AQ', 'AJ', 'AT', 'A9', 'KQ', 'KJ', 'KT', 'QJ', 'QT', 'JT', 'T9',
              'QQ', 'JJ', 'TT', '99', '88', '77', '66', '55', '44', '33', '22']
CALL_CARD_SUITS = ['A9', 'A8', 'A7', 'A6', 'A5', 'A4', 'A3', 'A2',
                   'KJ', 'KT', 'QJ', 'QT', 'Q9', 'JT', 'J9', 'T9']


def do_action(game: Game):
    action = river(game)
    if not action:
        action = turn(game)
    if not action:
        action = flop(game)
    if not action:
        action = pre_flop(game)
    return action


def pre_flop(game: Game):
    if game.card1 and game.card2:
        c1 = game.card1[0:1] + game.card2[0:1]
        c2 = game.card2[0:1] + game.card1[0:1]
        if c1 in RAISE_CARDS or c2 in RAISE_CARDS:
            return Action.Raise
        if c1 in CALL_CARDS or c2 in CALL_CARDS:
            return Action.Call
        if c1 in CALL_CARD_SUITS or c2 in CALL_CARD_SUITS:
            if game.card1[1] == game.card2[1]:
                return Action.Check
        return Action.Check


def flop(game: Game):
    return []


def turn(game: Game):
    return []


def river(game: Game):
    return []
