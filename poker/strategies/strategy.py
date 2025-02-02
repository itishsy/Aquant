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
            hand.board = [game.card3, game.card4, game.card5]
            if game.card6:
                hand.board.append(game.card6)
                if game.card7:
                    hand.board.append(game.card7)

        opponent_range = self.opponent_ranges(game)
        hand_score = hand.get_score()
        win_rate = hand.win_rate(opponent_range)
        print('hand_score==> {} , win_rate ==> {}'.format(hand_score, win_rate))
        args = {
            'stage': game.stage,
            'hand_score': hand_score,
            'pool': int(game.sections[-1].pool/Decimal(str(BB))),
            'seat': game.seat,
            'win_rate': win_rate
        }
        act = eval_cond(self.action_cond, args)
        game.action = act

    def opponent_ranges(self, game):
        """
        评估玩家的手牌范围
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


