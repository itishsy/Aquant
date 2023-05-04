from enum import Enum


class Strategy(Enum):
    reverse = "反转",
    gold_cross = "零轴上方金叉",
    reverse_to_gold_cross = "（次级别）反转形成金叉",
    gold_cross_from_reverse = "反转后的金叉"

    def __str__(self):
        return self.value
