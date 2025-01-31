from treys import Card, Evaluator, Deck
import numpy as np
import random
import copy

# 定义扑克牌的牌面和花色
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
suits = ['s', 'h', 'c', 'd']
deck = [rank + suit for rank in ranks for suit in suits]
hands_rate = {
    'AA': 88.88, 'KK': 85.52,
    'QQ': 79.10, 'AKs': 78.60, 'JJ': 77.10, 'TT': 73.61, 'AQs': 71.88, 'AKo': 70.71,
    'AJs': 66.70, 'AQo': 65.80, 'KQs': 63.81, 'ATs': 62.50, 'KJs': 60.90, '99': 60.52, '88': 60.31,
    'AJo': 59.98, 'QJs': 59.88, 'KQo': 59.78, 'ATo': 59.68, 'KTs': 59.58, 'QTs': 59.48, 'JTs': 59.38,
    '77': 58.60, '66': 58.20, 'KJo': 57.60, 'QJo': 56.50, '55': 56.30, '44': 56.20, 'KTo': 55.80,
    'T9s': 55.60, 'QTo': 55.10, 'A9s': 53.80, 'A8s': 53.74, '33': 53.10, '22': 53.01, 'JTo': 52.80,
    'J9s': 52.70, 'A7s': 52.50, 'A6s': 52.40, 'A5s': 52.30, 'A4s': 52.20, 'A3s': 52.10, 'A2s': 52.05,
    '98s': 51.80, '97s': 51.70, '87s': 51.50, '86s': 51.40, '76s': 50.70,
    '75s': 50.50, '65s': 50.40, '54s': 50.30, '43s': 50.20,
    'A9o': 42.10, 'A8o': 41.80, 'A7o': 41.70, 'A6o': 41.60, 'A5o': 41.50, 'A4o': 41.40, 'A3o': 41.30, 'A2o': 41.20,
    'K9o': 41.10, 'K9s': 42.10, 'K8s': 36.10, 'K8o': 35.10, 'K7o': 35.10, 'K7s': 36.10, 'K6s': 36.10, 'K6o': 35.10,
    'K5o': 35.10, 'K5s': 35.10, 'K4s': 35.10, 'K4o': 35.10, 'K3s': 35.10, 'K3o': 35.10, 'K2o': 35.10, 'K2s': 35.10,
    'Q9o': 41.10, 'Q9s': 42.10, 'Q8o': 35.10, 'Q8s': 39.10, 'Q7s': 35.10, 'Q7o': 35.10, 'Q6s': 35.10, 'Q6o': 35.10,
    'Q5o': 35.10, 'Q5s': 42.10, 'Q4o': 35.10, 'Q4s': 35.10, 'Q3s': 35.10, 'Q3o': 35.10, 'Q2s': 35.10, 'Q2o': 35.10,
    'J9o': 40.10, 'J8o': 35.10, 'J8s': 36.10, 'J7s': 36.10, 'J7o': 35.10, 'J6o': 35.10, 'J6s': 35.10, 'J5s': 35.10,
    'J5o': 35.10, 'J4s': 35.10, 'J4o': 35.10, 'J3s': 35.10, 'J3o': 35.10, 'J2o': 35.10, 'J2s': 35.10, 'T9o': 40.10,
    'T8o': 35.10, 'T8s': 39.10, 'T7s': 35.10, 'T7o': 35.10, 'T6o': 35.10, 'T6s': 35.10, 'T5s': 35.10, 'T5o': 35.10,
    'T4o': 35.10, 'T4s': 35.10, 'T3o': 35.10, 'T3s': 35.10, 'T2s': 35.10, 'T2o': 35.10, '98o': 36.10, '97o': 35.10,
    '96s': 36.10, '96o': 35.10, '95s': 35.10, '95o': 35.10, '94o': 35.10, '94s': 35.10, '93o': 35.10, '93s': 35.10,
    '92s': 35.10, '92o': 35.10, '87o': 35.10, '86o': 35.10, '85s': 35.10, '85o': 35.10, '84o': 35.10, '84s': 35.10,
    '83s': 35.10, '83o': 35.10, '82o': 35.10, '82s': 35.10, '76o': 35.10, '75o': 35.10, '74s': 35.10, '74o': 35.10,
    '73o': 35.10, '73s': 35.10, '72s': 35.10, '72o': 35.10, '65o': 35.10, '64o': 35.10, '64s': 35.10, '63s': 35.10,
    '63o': 35.10, '62o': 35.10, '62s': 35.10, '54o': 35.10, '53o': 35.10, '53s': 35.10, '52o': 35.10, '52s': 35.10,
    '43o': 35.10, '42o': 35.10, '42s': 35.10, '32o': 35.10, '32s': 35.10,
}


def card_index(card):
    rank = card[:-1]
    return ranks.index(rank)


def card_value(card):
    num = card[0]
    val = 0
    if num == 'T':
        val = val + 10
    elif num == 'J':
        val = val + 11
    elif num == 'Q':
        val = val + 12
    elif num == 'K':
        val = val + 13
    elif num == 'A':
        val = val + 14
    else:
        val = val + int(num)
    return val


class Cards:

    Straight_Flush = 9*10000
    Four_Of_A_Kind = 8*10000
    Full_House = 7*10000
    Flush = 6*10000
    Straight = 5*10000
    Three_Of_A_Kind = 4*10000
    Two_Pair = 3*10000
    Pair = 2*10000
    High_Card = 10000

    def __init__(self, hand):
        self.hand = hand
        current_deck = deck.copy()
        current_deck.remove(hand[0])
        current_deck.remove(hand[1])
        self.deck = current_deck

    def lookup(self, board, hand):
        from itertools import combinations
        score = 0
        for combination in combinations(hand + board, 5):
            five_score = self.five_card(list(combination))
            if five_score > score:
                score = five_score
        return score

    def win_rate(self, opponent_range, board=None):
        wins = 0
        num_simulations = 10000
        for _ in range(num_simulations):
            # 从对家的底牌范围中随机抽取手牌
            opponent_hand = opponent_range[np.random.randint(0, len(opponent_range))]

            current_deck = self.deck.copy()
            current_deck.remove(opponent_hand[0:2])
            current_deck.remove(opponent_hand[2:4])
            cur_board = board
            if not cur_board:
                cur_board = random.sample(current_deck, 5)
            elif len(board) < 5:
                for c in board:
                    current_deck.remove(c)
                cur_board = board + random.sample(current_deck, 5 - len(board))

            # 计算牌力
            strength1 = self.lookup(cur_board, self.hand)
            strength2 = self.lookup(cur_board, [opponent_hand[0:2], opponent_hand[2:4]])
            if strength1 > strength2:
                wins += 1
        return wins / num_simulations

    def five_card(self, cards):
        # 先将牌按牌面数值大小排序
        sorted_cards = sorted(cards, key=card_index)

        # 获取牌面和花色列表
        ranks_list = [card[:-1] for card in sorted_cards]
        suits_list = [card[-1] for card in sorted_cards]

        # 判断是否同花顺
        is_straight = False
        is_flush = len(set(suits_list)) == 1
        straight_ranks = [ranks.index(rank) for rank in ranks_list]
        if max(straight_ranks) - min(straight_ranks) == 4 and len(set(straight_ranks)) == 5:
            is_straight = True
        if is_straight and is_flush:
            return self.Straight_Flush + card_value(sorted_cards[-1])

        # 判断是否四条
        rank_counts = {}
        for rank in ranks_list:
            rank_counts[rank] = rank_counts.get(rank, 0) + 1
        for count in rank_counts.values():
            if count == 4:
                four_rank = [r for r in rank_counts if rank_counts[r] == 4][0]
                remaining_cards = [c for c in sorted_cards if c[:-1] != four_rank]
                # return '四条', [four_rank + suits_list[0]] * 4 + remaining_cards[:1]
                return self.Four_Of_A_Kind + card_value(four_rank)*100 + card_value(remaining_cards[-1])

        # 判断是否葫芦（三条加一对）
        three_ranks = [r for r in rank_counts if rank_counts[r] == 3]
        two_ranks = [r for r in rank_counts if rank_counts[r] == 2]
        if three_ranks and two_ranks:
            # return "葫芦", [r + suits_list[0] for r in three_ranks + two_ranks]
            return self.Full_House + card_value(three_ranks[0])*100 + card_value(two_ranks[0])

        # 判断是否同花
        if is_flush:
            # return "同花", sorted_cards[:5]
            return self.Flush + card_value(sorted_cards[-1])

        # 判断是否顺子
        if is_straight:
            # return "顺子", sorted_cards[:5]
            return self.Straight + card_value(sorted_cards[-1])

        # 判断是否三条
        if 3 in rank_counts.values():
            three_rank = [r for r in rank_counts if rank_counts[r] == 3][0]
            remaining_cards = [c for c in sorted_cards if c[:-1] != three_rank]
            # return "三条", [three_rank + suits_list[0]] * 3 + remaining_cards[:2]
            return self.Three_Of_A_Kind + card_value(three_rank)*100 + card_value(remaining_cards[-1])

        # 判断是否两对
        pair_count = 0
        pair_ranks = []
        for count in rank_counts.values():
            if count == 2:
                pair_count += 1
                pair_ranks.append([r for r in rank_counts if rank_counts[r] == 2])
        if pair_count == 2:
            # return "两对", [r + suits_list[0] for r in pair_ranks[0] + pair_ranks[1]]
            c1 = card_value(pair_ranks[0][0])
            c2 = card_value(pair_ranks[0][1])
            return self.Two_Pair + max(c1, c2)*100 + min(c1, c2)

        # 判断是否一对
        if pair_count == 1:
            pair_rank = [r for r in rank_counts if rank_counts[r] == 2][0]
            remaining_cards = [c for c in sorted_cards if c[:-1] != pair_rank]
            # return "一对", [pair_rank + suits_list[0]] * 2 + remaining_cards[:3]
            return self.Pair + card_value(pair_rank)*100 + card_value(remaining_cards[-1])

        # 如果都不是，就是高牌
        # return "高牌", sorted_cards[:5]
        return (((self.High_Card + (card_value(sorted_cards[-1])-5)*1000
                + (card_value(sorted_cards[-2])-5)*100)
                + (card_value(sorted_cards[-3])-5)*10)
                + (card_value(sorted_cards[-4])-5))

    def to_string(self, val):
        m2 = val // 100 % 100 - 2   # 中间2位
        t2 = val % 100 - 2          # 最后2位
        if val >= self.Straight_Flush:
            s = '同花顺' + ranks[t2]
        elif val >= self.Four_Of_A_Kind:
            s = '四条' + ranks[m2] + ',' + ranks[t2]
        elif val >= self.Full_House:
            s = '葫芦' + ranks[m2] + ',' + ranks[t2]
        elif val >= self.Flush:
            s = '同花' + ranks[t2]
        elif val >= self.Straight:
            s = '顺子' + ranks[t2]
        elif val >= self.Three_Of_A_Kind:
            s = '三条' + ranks[m2] + ',' + ranks[t2]
        elif val >= self.Two_Pair:
            s = '两对' + ranks[m2] + ',' + ranks[t2]
        elif val >= self.Pair:
            s = '一对' + ranks[m2] + ',' + ranks[t2]
        else:
            s = ('高牌' + ranks[val // 1000 % 10 + 3] + ','
                 + ranks[val // 100 % 10 + 3] + ','
                 + ranks[val // 10 % 10 + 3] + ','
                 + ranks[val % 10 + 3])
        return s


class Hand:

    def __init__(self, card1, card2):
        self.evaluator = Evaluator()
        self.string = card1[0] + card2[0] if card_value(card1) > card_value(card2) else card2[0] + card1[0]
        self.short = self.string if card1[0] == card2[0] else (self.string + ('s' if card1[1] == card2[1] else 'o'))
        self.hand = [Card.new(card1),  Card.new(card2)]
        self.deck = Deck()
        self.board = []

    def set_board(self, *args):
        if 3 <= len(args) <= 5:
            for cd in args:
                self.board.append(Card.new(cd))

    def get_score(self):
        res = hands_rate.get(self.short)
        return 35.10 if res is None else res

    def eval(self):
        # 评估手牌
        score = self.evaluator.evaluate(self.board, self.hand)
        # 步骤 4: 获取牌型等级
        hand_class = self.evaluator.get_rank_class(score)
        # 步骤 5: 获取牌型名称
        class_name = self.evaluator.class_to_string(hand_class)
        return score, hand_class, class_name

    def win_rate(self, opponent_range, num_simulations=10000):
        wins = 0
        opponent_wins = 0
        for _ in range(num_simulations):
            # 从对家的底牌范围中随机抽取手牌
            opponent_cards = opponent_range[np.random.randint(0, len(opponent_range))]
            opponent_hand = [Card.new(opponent_cards[0:2]), Card.new(opponent_cards[2:4])]
            # 初始化牌堆
            # cur_deck = Deck()
            self.deck.shuffle()
            # 从牌堆中移除已出现的牌
            used_card = self.hand + opponent_hand + self.board
            for card in used_card:
                self.deck.cards.remove(card)

            # used_card = self.hand + opponent_hand
            # remaining_deck = [Card.new(card) for card in deck if card not in used_card]
            # random.shuffle(remaining_deck)
            # 洗牌
            # cur_deck.shuffle()
            # board = remaining_deck[:5]

            board = self.board + self.deck.draw(5 - len(self.board))
            # 计算牌力
            strength1 = self.evaluator.evaluate(self.hand, board)
            strength2 = self.evaluator.evaluate(opponent_hand, board)
            if strength1 < strength2:
                wins += 1
            elif strength1 > strength2:
                opponent_wins += 1
        return wins / num_simulations, opponent_wins / num_simulations


kk = Hand('Ks', 'Kd')
# hand.set_board('Ks', 'Kc', 'Qc', 'Qd')
# rate = kk.win_rate(['Ts5c', 'AsAc'])
rate = kk.get_score()
# cards1 = Cards('Ts', 'Qs', '7c', 'Kc', '4d', 'Jh', '2c')
# val1 = cards1.lookup()
# print(val1, cards1.to_string(val1))

# kk = Cards(['Ks', 'Kd'])
# rate = kk.win_rate(['AsKc'])
print(rate)


