# 定义扑克牌的牌面和花色
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
suits = ['s', 'h', 'c', 'd']


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


def two_card_str(card1, card2):
    v1 = card_value(card1)
    v2 = card_value(card2)
    cv = card1[0] + card2[0] if v1 > v2 else card2[0] + card1[0]
    if card1[1] == card2[1]:
        return cv + 's'
    return cv


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

    def __init__(self, *args):
        self.cards = []
        for c in args:
            if c:
                self.cards.append(c)

    def lookup(self):
        size = len(self.cards)
        if size == 5:
            return self.five_card_type(self.cards)
        else:
            from itertools import combinations
            card_type_value = 0
            for combination in combinations(self.cards, 5):
                five_card_type_value = self.five_card_type(list(combination))
                if five_card_type_value > card_type_value:
                    card_type_value = five_card_type_value
            return card_type_value

    def five_card_type(self, cards):
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


cards1 = Cards('Ts', 'Qs', '7c', 'Kc', '4d', 'Jh', '2c')
val1 = cards1.lookup()
print(val1, cards1.to_string(val1))

