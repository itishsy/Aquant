import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models


# 生成52张牌的独热编码
def card_to_onehot(card):
    suits = ['H', 'D', 'C', 'S']  # 红桃、方块、梅花、黑桃
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    index = suits.index(card[1]) * 13 + ranks.index(card[0])
    onehot = np.zeros(52)
    onehot[index] = 1
    return onehot


# 示例
hand = ['As', 'Kd']
hand_onehot = np.concatenate([card_to_onehot(card) for card in hand])

# 假设玩家位置、下注金额、底池大小
position = 2
bet_amount = 100
pot_size = 500

# 对位置进行独热编码
position_onehot = np.zeros(6)  # 假设最多6个玩家
position_onehot[position] = 1

# 下注金额和底池大小进行归一化
bet_amount_normalized = bet_amount / 1000  # 假设最大下注为1000
pot_size_normalized = pot_size / 1000

# 合并所有信息
state = np.concatenate([hand_onehot, position_onehot, [bet_amount_normalized, pot_size_normalized]])



