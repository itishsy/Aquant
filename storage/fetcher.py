from datetime import datetime
import traceback
import storage.database as db
import storage.indicator as ind
import config as cfg
import efinance as ef
import logging


def fetch_code_dict():
    code_dict = db.query("SELECT `code`, `status` FROM `code_dict`")
    if len(code_dict) == 0:
        df = ef.stock.get_realtime_quotes(['沪A', '深A', 'ETF'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        df = df[df['name'].str.contains('ST') == False]
        for idx, row in df.iterrows():
            code = row['code']
            if (code[0:2] in cfg.prefix):
                db.create_stock_table(code)
                db.execute(db.get_connect(),
                           "INSERT INTO `code_dict` (`code`, `created`) VALUES ('{}', NOW());".format(code))
        code_dict = db.query("SELECT `code`, `status` FROM `code_dict`")
    code_dict = code_dict[code_dict['status'] > 0]
    print('fetch code dict. size:', len(code_dict))
    return code_dict


def update_code_date(code):
    updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.execute(db.get_connect(), "UPDATE `code_dict` SET `updated` = '{}' WHERE `code` = '{}'".format(updated, code))


def fetch_kline_data(stock_code, klt):
    begin_date = db.get_begin_datetime(stock_code, klt)
    k_data = ef.stock.get_quote_history(stock_code, klt=klt, beg=begin_date.replace('-', ''))
    print('{} [get history] code:{}, klt:{}, from:{}, size:{}'.format(datetime.now().strftime('%Y-%m-%d %H:%M'), stock_code, klt, begin_date, len(k_data)))
    if len(k_data) > 0:
        k_data = k_data.iloc[:, 0:8]
        k_data.columns = ['name', 'code', 'datetime', 'open', 'close', 'high', 'low', 'volume']
        s_sql = db.get_sql('insert_kline.sql').format(stock_code, klt)
        i_list = []
        for i, row in k_data.iterrows():
            i_list.append((row['datetime'],
                           row['open'],
                           row['close'],
                           row['high'],
                           row['low'],
                           row['volume'],
                           row['datetime']))
            if len(i_list) > 100:
                db.execute(db.get_connect(stock_code), s_sql, many=True, lis=i_list)
                i_list.clear()
        if len(i_list) > 0:
            db.execute(db.get_connect(stock_code), s_sql, many=True, lis=i_list)


def fetch_all():
    code_dict = fetch_code_dict()
    for i, row in code_dict.iterrows():
        code = row['code']
        for klt in [101, 102]:
            try:
                fetch_kline_data(code, klt)
                ind.update_mark(code, klt)
                ind.save_signal(code, klt)
            except Exception as e:
                traceback.print_exc()
                logging.error('{} fetch {} error: {}'.format(i, code, e))
            else:
                update_code_date(code)


if __name__ == '__main__':
    df = fetch_code_dict()
    print(df)