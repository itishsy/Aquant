import itertools
from collections import namedtuple

# 定义扑克牌
Card = namedtuple('Card', ['rank', 'suit'])
RANKS = '23456789TJQKA'
SUITS = 'shdc'  # s: spades, h: hearts, d: diamonds, c: clubs

# 生成所有牌
DECK = [Card(rank, suit) for rank in RANKS for suit in SUITS]

# 成手强度等级
HAND_RANKINGS = {
    "High Card": 1,
    "Pair": 2,
    "Two Pair": 3,
    "Three of a Kind": 4,
    "Straight": 5,
    "Flush": 6,
    "Full House": 7,
    "Four of a Kind": 8,
    "Straight Flush": 9,
    "Royal Flush": 10
}

# 计算成手强度
def evaluate_hand(cards):
    if len(cards) != 5:
        raise ValueError("Exactly 5 cards are required to evaluate a hand.")

    # 统计牌面和花色的频率
    rank_counts = {rank: 0 for rank in RANKS}
    suit_counts = {suit: 0 for suit in SUITS}
    for card in cards:
        rank_counts[card.rank] += 1
        suit_counts[card.suit] += 1

    # 检查是否是同花
    is_flush = any(count >= 5 for count in suit_counts.values())

    # 检查是否是顺子
    unique_ranks = sorted(set(card.rank for card in cards), key=lambda x: RANKS.index(x))
    is_straight = False
    if len(unique_ranks) >= 5:
        for i in range(len(unique_ranks) - 4):
            if RANKS.index(unique_ranks[i + 4]) - RANKS.index(unique_ranks[i]) == 4:
                is_straight = True
                break

    # 检查是否是皇家同花顺
    if is_flush and is_straight and unique_ranks[-1] == 'A':
        return "Royal Flush"

    # 检查是否是同花顺
    if is_flush and is_straight:
        return "Straight Flush"

    # 检查是否是四条
    if any(count == 4 for count in rank_counts.values()):
        return "Four of a Kind"

    # 检查是否是葫芦
    if any(count == 3 for count in rank_counts.values()) and any(count == 2 for count in rank_counts.values()):
        return "Full House"

    # 检查是否是同花
    if is_flush:
        return "Flush"

    # 检查是否是顺子
    if is_straight:
        return "Straight"

    # 检查是否是三条
    if any(count == 3 for count in rank_counts.values()):
        return "Three of a Kind"

    # 检查是否是两对
    if list(rank_counts.values()).count(2) >= 2:
        return "Two Pair"

    # 检查是否是对子
    if any(count == 2 for count in rank_counts.values()):
        return "Pair"

    # 否则是高牌
    return "High Card"

# 获取所有能赢过你的手牌范围
def get_winning_opponent_hands(your_hand, community_cards):
    # 你的成手
    your_best_hand = evaluate_hand(your_hand + community_cards)
    your_hand_rank = HAND_RANKINGS[your_best_hand]

    # 移除已知的牌（你的手牌和公共牌）
    known_cards = set(your_hand + community_cards)
    remaining_deck = [card for card in DECK if card not in known_cards]

    # 遍历所有可能的对手手牌组合
    winning_hands = []
    for opponent_hand in itertools.combinations(remaining_deck, 2):
        opponent_best_hand = evaluate_hand(list(opponent_hand) + community_cards)
        opponent_hand_rank = HAND_RANKINGS[opponent_best_hand]

        # 如果对手的成手强度高于你的成手强度
        if opponent_hand_rank > your_hand_rank:
            winning_hands.append(opponent_hand)

    return winning_hands

# 示例输入
your_hand = [Card('A', 's'), Card('K', 's')]
community_cards = [Card('Q', 's'), Card('J', 's'), Card('T', 's'), Card('9', 'd'), Card('2', 'h')]

# 获取能赢过你的手牌范围
winning_hands = get_winning_opponent_hands(your_hand, community_cards)

# 输出结果
print(f"你的成手: {evaluate_hand(your_hand + community_cards)}")
print(f"能赢过你的手牌范围（共 {len(winning_hands)} 种）:")
for hand in winning_hands:
    print(hand)