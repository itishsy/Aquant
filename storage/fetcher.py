from datetime import datetime,timedelta
from storage.kline import upset_data
from storage.agu import fetch_error
import storage.indicator as idc
import config as cfg
import efinance as ef
import json


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

    with open(cfg.work_path + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
        del code_dict["key_update"]
        return code_dict


def update_storage_date(code, val=None):
    with open(cfg.work_path + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)

    if val is None:
        now = datetime.now()
        if now.hour < 15:
            code_dict[code] = (now + timedelta(days=-1)).strftime('%Y-%m-%d')
        else:
            code_dict[code] = now.strftime('%Y-%m-%d')
    else:
        code_dict[code] = val

    with open(cfg.work_path + r"//storage//code.json", 'w', encoding='utf-8') as f:
        json.dump(code_dict, f, ensure_ascii=False)


def last_storage_date(code):
    with open(cfg.work_path + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)
    if code in code_dict:
        return code_dict[code]
    return "-1"


def start_fetch(prefix='*', begin='*'):
    code_dict = fetch_code_dict()
    for code in code_dict:
        begin_date = '' if (begin == '*') else last_storage_date(code)
        try:
            if (prefix == '*') | code.startswith(prefix):
                upset_size = upset_data(code, begin_date)
                print("[updated] code:{}, begin:{}, result:{}".format(code, begin_date, upset_size))
                if upset_size > 0:
                    update_storage_date(code)
                if begin == '':
                    idc.mark(code, klt=102, begin='2010-01-01')
                    idc.mark(code, klt=101)
        except:
            fetch_error(code, begin_date)
            print('fetch {} error'.format(code))


if __name__ == '__main__':
    start_fetch()
