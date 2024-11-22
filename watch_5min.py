from datetime import datetime
import logging
import time
from candles.fetcher import fetch_data
from candles.marker import mark
from signals.divergence import diver_top, diver_bottom
import tkinter as tk
from tkinter import messagebox
from models.symbol import Symbol


logging.basicConfig(format='%(asctime)s %(message)s', filename='d://aquant.log')
logging.getLogger().setLevel(logging.INFO)


def read_sta():
    sa = []
    s = ''
    try:
        with open('candles\st', 'r') as file:
            s = file.read()
    except FileNotFoundError:
        print("文件不存在或路径错误")
    except Exception as e:
        print("发生错误：", str(e))
    if s != '':
        sa = s.split(",")
    return sa


def show_dialog(info):
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    root.attributes("-topmost", True)  # 将消息框置顶显示
    r = messagebox.askokcancel("请确认", "是否要继续？ info：" + info)
    root.destroy()
    return r


if __name__ == '__main__':
    flag = False
    sig_dts = []
    while True:
        sta = read_sta()
        if len(sta) > 0:
            for st in sta:
                if flag:
                    break
                freq = 5
                candles = fetch_data(st, freq)
                candles = mark(candles)
                dbs = diver_bottom(candles)
                if len(dbs) > 0 and dbs[-1].dt not in sig_dts:
                    dt = dbs[-1].dt
                    sig_dts.append(st+dt)
                    print('[{}] {}: bottom sig:{} freq: {}'.format(datetime.now().strftime("%H:%M"), st[-3:], dt, freq))
                    if dt > datetime.now().strftime("%Y-%m-%d 00:00:01"):
                        result = show_dialog(st[-2:]+' ' + str(freq) + 'b ' + str(dt))
                        if not result:
                            flag = True
                            break
                dts = diver_top(candles)
                if len(dts) > 0 and dts[-1].dt not in sig_dts:
                    dt = dts[-1].dt
                    sig_dts.append(st+dt)
                    print('[{}] {}: top sig:{} freq: {} '.format(datetime.now().strftime("%H:%M"), st[-3:], dt, freq))
                    if dt > datetime.now().strftime("%Y-%m-%d 00:00:01"):
                        result = show_dialog(st[-2:]+' ' + str(freq) + 's ' + str(dt))
                        if not result:
                            flag = True
                            break
            if flag:
                print('用户取消')
                break
        else:
            print("无数据")
            break
        time.sleep(60 * 5)
