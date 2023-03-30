import database as db
from datetime import datetime,timedelta
import efinance as ef
import json


def upset_data(stock_code):
    table_name = 'k_{}'.format(stock_code)
    begin_date = last_storage_date(stock_code)
    if begin_date == "-1":
        return
    if begin_date == "":
        db.create(table_name)
        print('create table name:{}'.format(table_name))
        begin_date = '2000-01-01'
    if begin_date < datetime.now().strftime('%Y-%m-%d'):
        print('get quote history:{}'.format(stock_code))
        for klt in [101, 102, 103, 60, 30, 15]:
            k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin_date.replace('-', ''))
            k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume', 'cje', 'zf', 'rise', 'zde', 'hsl']
            k_data.drop(['name', 'code'], axis=1, inplace=True)
            k_data['klt'] = klt
            db.insert(k_data, table_name)
        update_storage_date(stock_code)


def fetch_code_dict():
    key_update = last_storage_date("key_update")
    cur_month = datetime.now().strftime('%Y%m')
    if cur_month != key_update:
        df = ef.stock.get_realtime_quotes(['沪A','深A','ETF'])
        df = df.iloc[:,0:2]
        df.columns = ['code', 'name']
        df = df[df['name'].str.contains('ST') == False]

        for idx, row in df.iterrows():
            c = row['code']
            if c.startswith('00') | c.startswith('30') | c.startswith('60') | c.startswith('51'):
                last_storage = last_storage_date(c)
                if last_storage == "-1":
                    update_storage_date(c, "")

        update_storage_date("key_update",cur_month)

    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
        del code_dict["key_update"]
        return code_dict


def update_storage_date(code, val=None):
    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)

    if val is None:
        now = datetime.now()
        if now.hour < 15:
            code_dict[code] = (now + timedelta(days=-1)).strftime('%Y-%m-%d')
        else:
            code_dict[code] = now.strftime('%Y-%m-%d')
    else:
        code_dict[code] = val

    with open("code.json", 'w', encoding='utf-8') as f:
        json.dump(code_dict, f, ensure_ascii=False)


def last_storage_date(code):
    with open("code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
    if code in code_dict:
        return code_dict[code]
    return "-1"


if __name__ == '__main__':
    code_dict = fetch_code_dict()
    for code in code_dict:
        upset_data(code)