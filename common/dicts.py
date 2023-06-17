
def freq_level(lev=None):
    if lev is None:
        return [(1, [5]), (2, [5, 15]), (3, [15, 30, 60]), (4, [101]), (5, [5, 15, 30, 60, 120, 101]), (6, [102])]
    if lev == 1:
        # 30C
        return [5]
    elif lev == 2:
        # 60C
        return [5, 15]
    elif lev == 3:
        # 上涨中枢
        return [15, 30, 60]
    elif lev == 4:
        return [101]
    elif lev == 5:
        return [5, 15, 30, 60, 120, 101]
    elif lev == 6:
        return [102]
    else:
        return []


def choice_strategy(key=None):
    if key is None:
        return [('uar', '趋势调整'), ('drc', '趋势反转确认'), ('hot', '热点题材')]
    if key == 'uar':
        return '趋势调整'
    elif key == 'drc':
        return '趋势反转确认'
    elif key == 'hot':
        return '热点题材'
    else:
        return ''
