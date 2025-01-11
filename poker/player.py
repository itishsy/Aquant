from poker.entities import Player


class PlayerAction:
    stage = 0
    round = 0
    action = ''
    amount = 0.0


def eval_player_actions(sections, idx):
    sec = sections[-1]
    player = Player()
    player.name = eval('sec.player{}'.format(idx))
    player.seat = (sec.seat + idx) % 6
    for i in range(len(sections)):
        sec = sections[i]
        pool = sec.pool
