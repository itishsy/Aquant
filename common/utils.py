from datetime import datetime


def dt_format(dt, fm='%Y-%m-%d'):
    if dt.find(':') > 0:
        sdt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
    else:
        sdt = datetime.strptime(dt, '%Y-%m-%d')
    return sdt.strftime(fm)


def now_ymd():
    now = datetime.now()
    ymd = datetime(year=now.year, month=now.month, day=now.day)
    return ymd


def now_ymd_str():
    ymd = now_ymd()
    return ymd.strftime('%Y-%m-%d')

