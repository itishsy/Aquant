from datetime import datetime


def dt_format(dt, fm='%Y-%m-%d'):
    if dt.find(':') > 0:
        sdt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
    else:
        sdt = datetime.strptime(dt, '%Y-%m-%d')
    return sdt.strftime(fm)


def freq_level(lev=None):
    if lev is None:
        return [(1, [5, 15]), (2, [15, 30]), (3, [30, 60]), (4, [60, 120]), (5, [101]), (6, [102])]
    if lev == 1:
        return [5, 15]
    elif lev == 2:
        return [15, 30]
    elif lev == 3:
        return [30, 60]
    elif lev == 4:
        return [60, 120]
    elif lev == 5:
        return [101]
    elif lev == 6:
        return [102]
    else:
        return []
