from engines.engine import job_engine, Fetcher
from models.symbol import Symbol
from datetime import datetime
from candles.finance import clean_data, fetch_and_save
import efinance as ef


@job_engine
class candles(Fetcher):

    def fetch(self):
        now = datetime.now()
        freq = [101, 120, 60, 30]
        clean = False
        if now.weekday() == 5:
            freq.append(102)
        if now.day == 1:
            clean = True
            freq.append(103)

        sbs = Symbol.actives()
        count = 0
        for sb in sbs:
            try:
                print('[{}] {} fetch candles [{}] start!'.format(datetime.now(), count, sb.code))
                if clean:
                    clean_data(sb.code)
                for fr in freq:
                    fetch_and_save(sb.code, fr)
                print('[{}] {} fetch candles [{}] done!'.format(datetime.now(), count, sb.code))
                count = count + 1
            except Exception as ex:
                print('fetch candles [{}] error!'.format(sb.code), ex)
        print('[{}] fetch all done! elapsed time:{}'.format(datetime.now(), datetime.now() - now))


@job_engine
class symbols(Fetcher):

    def fetch(self):
        df = ef.stock.get_realtime_quotes(['沪A', '深A'])
        df = df.iloc[:, 0:2]
        df.columns = ['code', 'name']
        for i, row in df.iterrows():
            code = row['code']
            name = row['name']
            if 'ST' in row['name'] or str(code).startswith('688'):
                continue
            else:
                series = ef.stock.get_base_info(row['code'])
                print('upset symbol code =', row['code'], ',name =', row['name'], i)
                if Symbol.select().where(Symbol.code == code).exists():
                    symbol = Symbol.get(Symbol.code == code)
                else:
                    symbol = Symbol()
                    symbol.code = code
                    symbol.updated = datetime.now()
                symbol.name = name
                for k in series.keys():
                    val = series[k]
                    if str(k).startswith('净利润'):
                        symbol.profit = val if isinstance(val, float) else 0.0
                    elif str(k).startswith('总市值'):
                        symbol.total = val if isinstance(val, float) else 0.0
                    elif str(k).startswith('流通市值'):
                        symbol.circulating = val if isinstance(val, float) else 0.0
                    elif str(k).startswith('所处行业'):
                        symbol.industry = val
                    elif str(k).startswith('市盈率'):
                        symbol.pe = val if isinstance(val, float) else 0.0
                    elif k == '市净率':
                        symbol.pb = val if isinstance(val, float) else 0.0
                    elif k == 'ROE':
                        symbol.roe = val if isinstance(val, float) else 0.0
                    elif k == '毛利率':
                        symbol.gross = val if isinstance(val, float) else 0.0
                    elif k == '净利率':
                        symbol.net = val if isinstance(val, float) else 0.0
                    elif k == '板块编号':
                        symbol.sector = val
                if symbol.industry in ['银行', '房地产开发', '房地产服务', '装修建材']:
                    symbol.status = 0
                    symbol.comment = '剔除行业'
                # elif symbol.total < 5000000000 or symbol.circulating < 3000000000:
                #     symbol.status = 0
                #     symbol.comment = '小市值'
                else:
                    symbol.status = 1
                symbol.updated = datetime.now()
                symbol.save()

