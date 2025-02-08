from poker.game import Game, Section
from poker.strategies.strategy import Strategy


def test_strategy(code):
    sections = Section.select().where(Section.game_code == code).order_by(Section.id)
    strategy = Strategy()
    game = None
    if len(sections) > 0:
        idx = 0
        for sec in sections:
            if idx == 0:
                game = Game(sec)
                print(game.get_info())
            else:
                game.append_section(sec)
            act = strategy.predict_action(game)
            print(act)
            idx = idx + 1


test_strategy('20250208152154')
