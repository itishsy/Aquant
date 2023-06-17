from datetime import datetime


def dt_format(dt, fm='%Y-%m-%d'):
    if dt.find(':') > 0:
        sdt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
    else:
        sdt = datetime.strptime(dt, '%Y-%m-%d')
    return sdt.strftime(fm)
