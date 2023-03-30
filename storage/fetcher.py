import database as db
from datetime import datetime,timedelta
import efinance as ef
import json


def upset_data(stock_code):
    table_name = 'k_{}'.format(stock_code)
    begin_date = last_storage_date(stock_code)
    print('begin_date:{}'.format(begin_date))
    if begin_date == "":
        db.create(table_name)
        begin_date = '2000-01-01'
    if begin_date < datetime.now().strftime('%Y-%m-%d'):
    #db.execute("DELETE FROM `{}` WHERE `datetime` >= '{}'".format(table_name, begin_date))
        for klt in [101, 102, 103, 60, 30, 15]:
            print('get history klt:{}'.format(klt))
            k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin_date.replace('-', ''))
            k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume', 'cje', 'zf', 'rise', 'zde', 'hsl']
            k_data.drop(['name', 'code'], axis=1, inplace=True)
            k_data['klt'] = klt
            db.insert(k_data, table_name)
        update_storage_date(stock_code)


def update_storage_date(code):
    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)

    now = datetime.now()
    if now.hour < 15:
        code_dict[code] = (now + timedelta(days=-1)).strftime('%Y-%m-%d')
    else:
        code_dict[code] = now.strftime('%Y-%m-%d')

    with open("code.json", 'w', encoding='utf-8') as f:
        json.dump(code_dict, f, ensure_ascii=False)


def last_storage_date(code):
    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
    if code in code_dict:
        return code_dict[code]
    return ""


if __name__ == '__main__':
    print('==========')
    upset_data('300035')