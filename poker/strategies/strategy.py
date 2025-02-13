import poker.game
from poker.card import Hand, suits
from poker.strategies.sorted_hands import hands_win_rate
from poker.config import BB
from decimal import Decimal
from itertools import combinations
import random


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
        self.children = []

    def append_child(self, exp, level):
        parent = fetch_by_level(self, level)
        if parent:
            cd = Cond(exp)
            cd.code = '{}{}'.format(parent.code, len(parent.children) + 1)
            cd.children = []
            parent.children.append(cd)


def eval_cond(cond, args):
    for co in cond.children:
        if not co.children:
            return co.exp.strip()
        if eval(co.exp, args):
            return eval_cond(co, args)


class Strategy:

    actions = 'strategies/actions.txt'
    ranges = 'strategies/ranges.txt'

    def __init__(self):
        self.action_cond = None
        self.range_cond = None
        self.action_args = {}
        self.range_args = {}
        try:
            with open(self.actions, 'r', encoding='utf-8') as file:
                line = file.readline()
                self.action_cond = Cond(line)
                while line:
                    line = file.readline()
                    self.action_cond.append_child(line.replace('\t', ''), line.count('\t'))
            with open(self.ranges, 'r', encoding='utf-8') as file:
                line = file.readline()
                self.range_cond = Cond(line)
                while line:
                    line = file.readline()
                    self.range_cond.append_child(line.replace('\t', ''), line.count('\t'))
        except FileNotFoundError:
            print(f"策略文件不存在,忽略")

    def predict_action(self, game):
        hand = Hand(game.card1, game.card2)
        if game.card3:
            hand.add_board(game.card3)
            hand.add_board(game.card4)
            hand.add_board(game.card5)
            if game.card6:
                hand.add_board(game.card6)
                if game.card7:
                    hand.add_board(game.card7)

        call_bb = int(game.sections[-1].call / BB)
        pot_bb = int(game.sections[-1].pool / BB)
        hand_score = hand.get_score()
        game.sections[-1].hand_score = hand_score

        win_rate = hand.win_rate(game.stage, self.predict_ranges(game))
        cev = 0 if call_bb == 0 else pot_bb * win_rate - (1 - win_rate) * call_bb
        if cev > 0:
            # call、raise
            if hand_score >= 80:
                """超强牌"""
                pass
            elif 80 > hand_score >= 70:
                """强牌"""
                pass
            elif 70 > hand_score >= 60:
                """中等牌"""
                pass
            elif 60 > hand_score >= 50:
                """机会牌"""
                pass
            elif 40 < hand_score < 50:
                """稍弱牌"""
                pass
            else:
                """弱牌"""
                pass
        elif cev == 0:
            # check、raise
            pass
        else:
            # fold、check、call
            return 'fold'

        if game.stage == 'PreFlop':
            """
            (1) hand_score>80，有raise，无call和fold选项。 raise随机选择bet大码
            (2) 80>hand_score>70，有raise、call, 无fold。 call量为中大码，选择call。 否则随机选择raise中大码
            (3) 70>hand_score>60，有raise、call、fold。 有call，按ev计算选择call和fold； 无call，随机选择raise中码
            (4) 60>hand_score>50，有call、fold，有条件raise。 ev计算call及fold，有位置时，min-raise随机bb(2,4)
            (5) hand_score<50, 有fold，有条件call。 有位置时，min-raise随机bb(2,4)
            """
            call_ev = 0 if call_bb == 0 else pot_bb * hand_score / 100 - (1 - hand_score / 100) * call_bb
            # print('hand_score==> {}'.format(hand_score))
            if hand_score >= 80:
                if call_bb < 3 and pot_bb < 4:
                    return 'raise:{}'.format(random.randint(2, 3))
                return 'raise:{}'.format(random.randint(pot_bb, pot_bb*2))
            elif 80 > hand_score >= 70:
                if call_bb > 0.0:
                    if call_bb < 3 or pot_bb < 4:
                        return 'raise:2'
                    if call_bb >= 3:
                        return 'call'
                return 'raise:{}'.format(random.randint(int(pot_bb/2), pot_bb))
            elif 70 > hand_score >= 60:
                if 0 < call_bb < 4:
                    return 'call'
                elif call_bb == 0:
                    return 'raise:{}'.format(random.randint(2, 5))
                else:
                    return 'call' if call_ev > 0 else 'fold'
            elif 60 > hand_score >= 50:
                if 4 > call_bb > 0:
                    return 'call'
                elif call_bb == 0:
                    return 'raise:{}'.format(random.randint(2, 4))
                else:
                    return 'raise' if call_ev > 0 else 'fold'
            elif 40 < hand_score < 50:
                if call_bb > 0.0:
                    if call_bb > 0 and game.seat in [1, 2, 6]:
                        return 'call'
                    else:
                        return 'fold'
                else:
                    return 'check'
            else:
                return 'fold'

            # args = {
            #     'stage': 'PreFlop',
            #     'hand_score': hand_score,
            #     'pool': pot,
            #     'seat': game.seat
            # }
            # act = eval_cond(self.action_cond, args)
        else:
            # 评估其他玩家的底牌范围
            strength = hand.get_strength()
            if strength > 0.5:
                # print('hand_strength ==> {}'.format(hand_strength))
                game.sections[-1].hand_strength = strength
                if call_bb > 0:
                    ev = pot_bb * strength - (1-strength) * call_bb
                    return 'call' if ev > 0 else 'fold'
                else:
                    if win_rate > 0.5:
                        return 'raise:{}'.format(random.randint(int(pot_bb * strength), int(pot_bb * 3/2)))
                    elif random.randint(1, 10) % 2 == 0:
                        return 'raise:{}'.format(random.randint(int(pot_bb * win_rate), pot_bb))
                    return 'check'
            else:
                win_rate = hand.win_rate(game)
                game.sections[-1].hand_strength = win_rate
                print('hand_strength ==> {}'.format(win_rate))
                if call_bb > 0:
                    ev = pot_bb * win_rate - (1 - win_rate) * call_bb
                    return 'call' if ev > 0 else 'fold'
                else:
                    win_rate = hand.win_rate(game)
                    if win_rate > 0.5:
                        return 'raise:{}'.format(random.randint(int(pot_bb * win_rate), int(pot_bb / 2)))
                    elif random.randint(1, 10) % 2 == 0:
                        return 'raise:{}'.format(random.randint(3, 8))
                    else:
                        return 'check'

    @staticmethod
    def predict_ranges(game):
        """
        手牌范围。评估翻牌前的手牌范围。跟底池大小、玩家行为习惯有关。
        :param game:
        :return:
        """

        player_pre_act = 'raise、call、3bet、check'   # 翻牌前行动。加注通常表示较强的手牌，而跟注可能意味着中等或投机性手牌。
        player_flop_act = '持续bet、check-raise'   # 翻牌后行动。
        player_balance = 100    # 筹码量。 短筹码玩家倾向于玩得更紧，而深筹码玩家可能更激进，尝试利用筹码优势进行诈唬或价值下注。
        player_amt = 6      # 翻牌后下注尺度。大额下注通常表示强牌或诈唬,小额下注可能意味着中等牌力或试探性下注
        player_style = '0, 1, 2'  # 历史行为。 紧凶、松凶、被动。紧凶玩家加注时通常有强牌，而松凶玩家可能用更宽的范围加注
        board_style = '单张成顺、单张成花、卡顺、三张花、'   # 牌面结构。 湿润牌面下注，对手可能有更多听牌或成牌

        # args = {
        #     'stage': game.stage,
        #     'call': game.sections[-1].call,
        #     'pool': int(game.sections[-1].pool / Decimal(str(BB))),
        # }
        # opponent_range_rate = eval_cond(self.range_cond, args).split('-')
        pot = int(game.sections[-1].pool / BB)
        if 1 < pot <= 3:
            opponent_range_rate = (0.2, 0.6)
        elif 3 < pot <= 10:
            opponent_range_rate = (0.4, 0.9)
        elif 10 < pot <= 50:
            opponent_range_rate = (0.5, 0.9)
        else:
            opponent_range_rate = (0.55, 0.9)

        game.sections[-1].opponent_range_rate = opponent_range_rate
        opponent_range = []
        for key, val in hands_win_rate.items():
            value = val / 100
            if opponent_range_rate[0] <= value <= opponent_range_rate[1]:
                if key[0] == key[1] or key[2] == 'o':
                    for combination in combinations(suits, 2):
                        opponent_range.append(key[0]+combination[0]+key[1]+combination[1])
                elif key[2] == 's':
                    for suit in suits:
                        opponent_range.append(key[0]+suit+key[1]+suit)
        return opponent_range

    def nuts_rate(self, game):
        """
        成牌概率。 一般来讲，成牌大小与下注金额相关。暂未考虑诈唬
        :param game:
        :return:
        """
        pass


def test_strategy(code):
    from poker.game import Game, Section
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
            print("{} : hand score --> {} action --> {}".format(
                game.stage, game.sections[-1].hand_score if game.stage == 'PreFlop' else game.sections[-1].hand_strength, act))
            idx = idx + 1


if __name__ == '__main__':
    test_strategy('20250208180018')
