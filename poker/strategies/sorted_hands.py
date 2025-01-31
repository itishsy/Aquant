from treys import Card, Evaluator
import itertools
import random

# 创建一副完整的牌
suits = ['h', 'd', 'c', 's']
ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
deck = [rank + suit for rank in ranks for suit in suits]

# 生成所有可能的两张手牌组合
all_hands = list(itertools.combinations(deck, 2))

# 创建评估器
evaluator = Evaluator()

# 模拟次数
num_simulations = 1000

hand_win_rates = {}

for hand in all_hands:
    wins = 0
    total = 0
    hand_cards = [Card.new(card) for card in hand]

    for _ in range(num_simulations):
        remaining_deck = [Card.new(card) for card in deck if card not in hand]
        random.shuffle(remaining_deck)
        board = remaining_deck[:5]

        score = evaluator.evaluate(board, hand_cards)

        # 假设与随机对手比较
        opponent_hand = remaining_deck[5:7]
        opponent_score = evaluator.evaluate(board, opponent_hand)

        if score < opponent_score:
            wins += 1
        total += 1

    win_rate = wins / total
    hand_win_rates[hand] = win_rate

# 根据胜率对所有手牌进行排序
sorted_hands = sorted(hand_win_rates.items(), key=lambda x: x[1], reverse=True)

# 输出部分结果示例（前 10 个）
for i, (hand, win_rate) in enumerate(sorted_hands[:2000], start=1):
    print(f"排名 {i}: 手牌 {hand}, 胜率 {win_rate * 100:.2f}%")


