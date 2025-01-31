# 定义牌面和花色
ranks = ['A', 'K', 'Q', 'J', 'T', '9', '8', '7', '6', '5', '4', '3', '2']
suits = ['h', 'd', 'c', 's']

unique_combinations = set()
for i in range(len(ranks)):
    for j in range(i, len(ranks)):
        if i == j:
            # 对子情况
            unique_combinations.add(ranks[i] * 2)
        else:
            # 同花色情况
            unique_combinations.add(f"{ranks[i]}{ranks[j]}s")
            # 不同花色情况
            unique_combinations.add(f"{ranks[i]}{ranks[j]}o")

# 按要求从大到小排序
sorted_combinations = sorted(unique_combinations, key=lambda x: (ranks.index(x[0]), ranks.index(x[1]) if len(x) > 2 else ranks.index(x[0])))

from poker.card import hands_rate

# 输出结果
for comb in sorted_combinations:
    if not hands_rate.get(comb):
        print("'{}': 35.10, ".format(comb))
