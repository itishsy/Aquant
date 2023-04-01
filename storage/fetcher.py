from datetime import datetime,timedelta
from kline import upset_data
import efinance as ef
import json
import os


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

    with open(os.path.abspath('..') + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
        del code_dict["key_update"]
        return code_dict


def update_storage_date(code, val=None):
    with open(os.path.abspath('..') + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)

    if val is None:
        now = datetime.now()
        if now.hour < 15:
            code_dict[code] = (now + timedelta(days=-1)).strftime('%Y-%m-%d')
        else:
            code_dict[code] = now.strftime('%Y-%m-%d')
    else:
        code_dict[code] = val

    with open(os.path.abspath('..') + r"//storage//code.json", 'w', encoding='utf-8') as f:
        json.dump(code_dict, f, ensure_ascii=False)


def last_storage_date(code):
    with open(os.path.abspath('..') + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
    if code in code_dict:
        return code_dict[code]
    return "-1"


if __name__ == '__main__':
    code_dict = fetch_code_dict()
    for code in code_dict:
        if code.startswith('-00008') | code.startswith('-60008') | code.startswith('300059') | code.startswith('510-'):
            begin_date = last_storage_date(code)
            res = upset_data(code,begin_date)
            print("[updated] code:{}, begin:{}, result:{}".format(code,begin_date,res))
            if res > 0:
                update_storage_date(code)