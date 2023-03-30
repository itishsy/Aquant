from storage.database import query


def read(stock_code, klt=101, beg='', end='', field='*', limit=-1, order_by='datetime'):
    sql = 'SELECT {} FROM {} WHERE klt={}'.format(field, 'k_{}'.format(stock_code), klt)
    if beg != '':
        sql = "{} AND `datetime` >= '{}'".format(sql, beg)
    if end != '':
        sql = "{} AND `datetime` <= '{}'".format(sql, end)
    sql = "{} ORDER BY {} ".format(sql, order_by)
    if limit > -1:
        sql = "{} LIMIT {}".format(sql,limit)
    return query(sql)