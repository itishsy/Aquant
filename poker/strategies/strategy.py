import poker.game
from poker.card import Hand, suits
from poker.strategies.sorted_hands import hands_win_rate
from poker.config import BB
from decimal import Decimal
from itertools import combinations


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

        call = float(game.sections[-1].call)
        if game.stage == 'PreFlop':
            """
            (1) hand_score>80，有raise，无call和fold选项。 raise随机选择bet大码
            (2) 80>hand_score>70，有raise、call, 无fold。 call量为中大码，选择call。 否则随机选择raise中大码
            (3) 70>hand_score>60，有raise、call、fold。 有call，按ev计算选择call和fold； 无call，随机选择raise中码
            (4) 60>hand_score>50，有call、fold，有条件raise。 ev计算call及fold，有位置时，min-raise随机bb(2,4)
            (5) hand_score<50, 有fold，有条件call。 有位置时，min-raise随机bb(2,4)
            """
            hand_score = hand.get_score()
            pot = int(game.sections[-1].pool/Decimal(str(BB)))

            if hand_score >= 80:
                return 'bet({},{})'.format(pot, pot*2)
            elif 80 > hand_score >= 70:
                return 'bet({},{})'.format(pot, pot*2)

            print('hand_score==> {}'.format(hand_score))
            args = {
                'stage': 'PreFlop',
                'hand_score': hand_score,
                'pool': pot,
                'seat': game.seat
            }
            act = eval_cond(self.action_cond, args)
            if act == 'fold' and call > 0.0 and game.seat in [1, 2, 6]:
                ev = pot * hand_score / 100 - (1 - hand_score / 100) * call
                if ev > 0:
                    act = 'call'
        else:
            # 评估其他玩家的底牌范围
            opponent_range = self.opponent_ranges(game)
            hand_strength = hand.get_strength()
            pool = game.sections[-1].pool
            if hand_strength > 0.5:
                if call > 0:
                    ev = pool * hand_strength - (1-hand_strength) * call
                    act = 'call' if ev > 0 else 'fold'
                else:
                    bet = int(Decimal(str(pool * hand_strength)) / Decimal(str(BB)))
                    max_bet = int(pool / Decimal(str(BB)))
                    act = 'bet({},{})'.format(bet, max_bet)
            else:
                win_rate = hand.win_rate(opponent_range)
                print('win_rate ==> {}'.format(win_rate))
                if call > 0:
                    ev = pool * win_rate - (1 - win_rate) * call
                    act = 'call' if ev > 0 else 'fold'
                else:
                    bet = int(Decimal(str(pool * win_rate)) / Decimal(str(BB)))
                    max_bet = int(pool / Decimal(str(BB)))
                    act = 'bet({},{})'.format(bet, max_bet)
        game.action = act

    def opponent_ranges(self, game):
        """
        评估对手的手牌范围
        :param game:
        :return:
        """

        player_pre_act = 'raise、call、3bet、check'   # 翻牌前行动。加注通常表示较强的手牌，而跟注可能意味着中等或投机性手牌。
        player_flop_act = '持续bet、check-raise'   # 翻牌后行动。
        player_balance = 100    # 筹码量。 短筹码玩家倾向于玩得更紧，而深筹码玩家可能更激进，尝试利用筹码优势进行诈唬或价值下注。
        player_amt = 6      # 翻牌后下注尺度。大额下注通常表示强牌或诈唬,小额下注可能意味着中等牌力或试探性下注
        player_style = '0, 1, 2'  # 历史行为。 紧凶、松凶、被动。紧凶玩家加注时通常有强牌，而松凶玩家可能用更宽的范围加注
        board_style = '单张成顺、单张成花、卡顺、三张花、'   # 牌面结构。 湿润牌面下注，对手可能有更多听牌或成牌

        args = {
            'stage': game.stage,
            'call': game.sections[-1].call,
            'pool': int(game.sections[-1].pool / Decimal(str(BB))),
        }
        rate_range = eval_cond(self.range_cond, args)
        min_rate = float(rate_range.split('-')[0])
        max_rate = float(rate_range.split('-')[1])
        opponent_range = []
        for key, value in hands_win_rate.items():
            if min_rate <= value <= max_rate:
                if key[0] == key[1] or key[2] == 'o':
                    for combination in combinations(suits, 2):
                        opponent_range.append(key[0]+combination[0]+key[1]+combination[1])
                elif key[2] == 's':
                    for suit in suits:
                        opponent_range.append(key[0]+suit+key[1]+suit)
        return opponent_range

