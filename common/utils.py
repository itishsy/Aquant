from datetime import datetime


def dt_format(dt, fm='%Y-%m-%d'):
    if dt.find(':') > 0:
        sdt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
    else:
        sdt = datetime.strptime(dt, '%Y-%m-%d')
    return sdt.strftime(fm)


def is_deal_time(freq):
    now = datetime.now()
    hm = now.hour * 100 + now.minute
    if now.weekday() < 5:
        if freq == 5 and hm in [946, 1006, 1016, 1036, 1056,
                                1106, 1116, 1136, 1316, 1331, 1346,
                                1406, 1421, 1436, 1451]:
            return True
        if freq == 15 and hm in [1001,1031,1101,1131,
                                 1331,1401,1431,1501]:
            return True
        if freq in [30,60] and hm in [1031, 1131, 1401, 1451]:
            return True
        if freq == 120 and hm in [1125, 1450, 1510]:
            return True
        if freq == 201 and hm in [1450, 1510]:
            return True
    return False
