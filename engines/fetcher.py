from engines.engine import job_engine, Fetcher
from models.symbol import Symbol
from datetime import datetime
from candles.finance import clean_data, fetch_and_save
import efinance as ef
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from models.review import Review
import time
import re


@job_engine
class Candles(Fetcher):

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
class Symbols(Fetcher):

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
                symbol.is_watch = 0
                symbol.created = datetime.now()
                symbol.save()


@job_engine
class DailyReview(Fetcher):
    def fetch(self):
        print("=====start driver=====")
        service = Service('C:\\Huangsy\\sourcecode\\pobotvenv\\msedgedriver.exe')
        driver = webdriver.Edge(service=service)
        # driver = webdriver.Chrome()

        review = Review()
        pan_data = ''
        # 成交量
        driver.get('https://www.cls.cn/finance')
        time.sleep(3)
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[2]/div[1]/div[2]')))
        pan_data = pan_data + '成交量：{} \n'.format(el.text)

        # 上证
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div[1]/div[1]/div/div[1]/a[1]/div')))
        el1 = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div[1]/div[1]/div/div[1]/a[2]/div')))
        sz_txt = '上证：{}({})'.format(el.text, el1.text)

        # 涨停数
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div/div[1]/div[2]/div/div/div/div[1]/div[2]/span[1]')))
        pan_data = pan_data + '涨停：{} \n'.format(el.text.replace('涨停', ''))

        # 上涨数
        driver.get('https://www.cls.cn/quotation')
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div[2]/div[3]/div[1]/span[2]')))
        pan_data = pan_data + '上涨：{} \n'.format(el.text)
        pan_data = pan_data + sz_txt

        review.pan_data = pan_data

        # 今日总结
        driver.get('https://www.cls.cn/subject/1139')
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/a')))
        review.pan_summary = el.text

        # 今日焦点
        driver.get('https://www.cls.cn/subject/1135')
        el = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(
            (By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/div[2]/div[1]/div[2]/div[1]/a')))
        review.pan_focus = el.text

        # 板块，流入流出
        driver.get('https://www.cls.cn/hotPlate')
        bk_in, bk_out = '', ''
        for i in range(1, 7):
            el_bk_name = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/a[{}]/div[2]'.format(i))
            el_bk_raise = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/a[{}]/div[3]/div[1]/span[2]'.format(i))
            el_bk_vol = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[1]/div[2]/a[{}]/div[3]/div[2]/span[2]'.format(i))
            if i < 4:
                bk_in = bk_in + ' ' + el_bk_name.text + ' ' + el_bk_raise.text + ' ' + el_bk_vol.text + '，'
            else:
                bk_out = bk_out + ' ' + el_bk_name.text + ' ' + el_bk_raise.text + ' ' + el_bk_vol.text + '，'
        review.bk_in = bk_in
        review.bk_out = bk_out

        # 板块，潜力
        bk_ql = ''
        for i in range(2, 5):
            el_bk_ql_name = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[1]/div[{}]/div[1]/div[2]/div[1]/a'
                .format(i))
            el_bk_ql_comment = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[1]/div[{}]/div[2]/ul/li/a'
                .format(i))
            el_bk_ql_gp1 = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[1]/div[{}]/div[3]/div[1]/a'
                .format(i))
            el_bk_ql_gp2 = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[1]/div[{}]/div[3]/div[2]/a'
                .format(i))
            bk_ql = bk_ql + '{}。{}, {}({})、{}({}) \n'.format(el_bk_ql_name.text, el_bk_ql_comment.text,
                                                             el_bk_ql_gp1.text, el_bk_ql_gp1.get_attribute('href'),
                                                             el_bk_ql_gp2.text, el_bk_ql_gp2.get_attribute('href'))
            print(el_bk_ql_name.text, el_bk_ql_comment.text,
                  el_bk_ql_gp1.text, el_bk_ql_gp1.get_attribute('href').split('=')[1],
                  el_bk_ql_gp2.text, el_bk_ql_gp2.get_attribute('href').split('=')[1])

        review.bk_ql = bk_ql

        # 板块 风口
        bk_fk = ''
        for i in range(2, 5):
            el_bk_fk_name = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[2]/div[{}]/div[1]/div[2]/div[1]/a'
                .format(i))
            el_bk_fk_comment = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[2]/div[{}]/div[2]/div'
                .format(i))
            el_bk_fk_gp = driver.find_element(
                By.XPATH, '//*[@id="__next"]/div/div[2]/div[2]/div[2]/div/div[2]/div[{}]/div[3]/div/a'
                .format(i))
            bk_fk = bk_fk + '{}。{}, {}({}) \n'.format(el_bk_fk_name.text, el_bk_fk_comment.text,
                                                      el_bk_fk_gp.text, el_bk_fk_gp.get_attribute('href'))
            print(el_bk_fk_name.text, el_bk_fk_comment.text,
                  el_bk_fk_gp.text, el_bk_fk_gp.get_attribute('href').split('=')[1])
        review.bk_fk = bk_fk

        # 热股
        gp_hot1 = ''
        driver.get('https://api3.cls.cn/quote/toplist')
        time.sleep(5)
        hot_list = driver.find_elements(By.CLASS_NAME, 'hot-list-right-box')
        j = 1
        for el in hot_list:
            els = el.find_elements(By.CLASS_NAME, 'openapp')
            flag = False
            print('No.', j)
            for el2 in els:
                final_str = re.sub(r"^\s+|\s+$", "", el2.text)
                txt = final_str.split('\n')
                if txt != '':
                    i = 0
                    for t in txt:
                        if t != '\n':
                            gp_hot1 = gp_hot1 + t
                            flag = True
                            print(i, t)
                            i = i + 1
            if flag:
                gp_hot1 = gp_hot1 + '\n'
            j = j + 1
        review.gp_hot1 = gp_hot1
        review.created = datetime.now()
        review.save()
