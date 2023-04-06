from datetime import datetime,timedelta
from storage.kline import upset_data
import storage.database as db
import storage.indicator as idc
import config as cfg
import efinance as ef
import json


def init_code_dict():
    with open(cfg.work_path + r"//storage//code.json", 'r', encoding='utf-8') as load_f:
        code_dict = json.load(load_f)

    key_update = code_dict['key_update']
    cur_month = datetime.now().strftime('%Y%m')
    if cur_month != key_update:
        df = ef.stock.get_realtime_quotes(['沪A','深A','ETF'])
        df = df.iloc[:,0:2]
        df.columns = ['code', 'name']
        df = df[df['name'].str.contains('ST') == False]

        for idx, row in df.iterrows():
            code = row['code']
            if (code[0:2] in cfg.prefix) and (code not in code_dict):
                update_storage_date(code, "")


def fetch_code_dict():
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

    if code == 'key_update':
        return code_dict['key_update']

    if code in code_dict:
        last_date = code_dict[code]
        if last_date == '':
            db.drop_table(code)
            db.create_stock_table(code)
            print('[create table] name:{}'.format(code))
            last_date = datetime((datetime.now().year-5), 1, 1).strftime('%Y-%m-%d')
        return last_date
    else:
        db.drop_table(code)
        return "-1"


def fetch_data(code):
    begin_date = last_storage_date(code)
    if (begin_date != '-1') and (begin_date < datetime.now().strftime('%Y-%m-%d')):
        fetch_size = upset_data(code, begin_date)
        print("[updated] code:{}, begin:{}, result:{}".format(code, begin_date, fetch_size))
        if fetch_size > 0:
            idc.macd_mark(code, 101, begin_date)
            idc.macd_mark(code, 102, begin_date)
            update_storage_date(code)
    else:
        print("code:{} is up to date".format(code))
    return begin_date


if __name__ == '__main__':
    print('fetch_data(300223)')
    fetch_data('300223')
