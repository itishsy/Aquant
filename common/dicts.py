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
        return [(0, '等待'), (1, '买入'), (2, '持有'), (3, '剔除'), (4, '弃用')]
    if key == 0:
        return '等待'
    if key == 1:
        return '买入'
    if key == 2:
        return '持有'
    if key == 3:
        return '剔除'
    if key == 4:
        return '弃用'
    return 'undefined'
