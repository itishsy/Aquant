def freq_level(ts=None):
    if ts is None:
        return [(0, [15, 30, 60]), (1, [5, 10, 15]), (2, [5, 10, 15, 30, 60]), (3, [101]), (4, [])]
    if ts == 0:
        return [15, 30, 60]
    if ts == 1:
        return [5, 10, 15]
    if ts == 2:
        return [5, 10, 15, 30, 60]
    if ts == 3:
        return [101]
    if ts == 4:
        return []
    return [5, 10, 15, 30, 60, 120, 101]


def choice_strategy(key=None):
    if key is None:
        return [('UAR', 'UAR'), ('DRC', 'DRC'), ('HOT', 'HOT')]
    if key == 'UAR':
        return 'UAR'
    if key == 'DRC':
        return 'DRC'
    if key == 'HOT':
        return 'HOT'
    return 'undefined'


def choice_status(key=None):
    if key is None:
        return [(0, '失效'), (1, '有效')]
    if key == 0:
        return '失效'
    if key == 1:
        return '有效'
    return 'undefined'


def ticket_status(key=None):
    if key is None:
        return [(0, '观察'), (1, '买入'), (2, '持有'), (3, '剔除'), (4, '弃用')]
    if key == 0:
        return '观察'
    if key == 1:
        return '买入'
    if key == 2:
        return '持有'
    if key == 3:
        return '剔除'
    if key == 4:
        return '弃用'
    return 'undefined'


def trade_type(key=None):
    if key is None:
        return [(0, '买入'), (1, '卖出')]
    if key == 0:
        return '买入'
    if key == 1:
        return '卖出'
    return 'undefined'


def single_source(key=None):
    if key is None:
        return [(0, '背离'), (1, '背驰'), (2, '量价背离'), (3, '分型'), (4, '量能')]
    if key == 0:
        return '背离'
    if key == 1:
        return '背驰'
    if key == 2:
        return '量价背离'
    if key == 3:
        return '分型'
    if key == 4:
        return '量能'
    return 'undefined'
