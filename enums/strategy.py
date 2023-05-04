from enum import Enum


class Strategy(Enum):
    reverse = "反转",
    gold_cross = "金叉",
    gold_cross_reverse = "金叉反转",
    gold_cross_after_reverse = "反转后的第一个金叉"

    def __str__(self):
        return self.value
