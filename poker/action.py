import time

import pyautogui
import random
from poker.config import *


class Action:

    def __init__(self, act, cal):
        self.act = None
        if act:
            act = act.strip()
            self.cal = cal
            if act in ['fold', 'call', 'check', 'allin']:
                self.act = act
            elif 'bet' in act:
                self.act = 'bet'
                self.val = act.replace('bet', '')

    def do(self):
        if self.act:
            method = getattr(self, self.act)
            method()
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(100, 150) - 300,
                         duration=0.8)  # duration 参数表示鼠标移动的时间

    @staticmethod
    def fold():
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def check():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def call():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    def bet(self):
        if self.val:
            val_range = eval(self.val)
            if self.call:
                if float(val_range[0]) * BB <= self.cal <= float(val_range[1]) * BB:
                    self.call()
                    return
                elif float(val_range[1]) * BB < self.cal:
                    self.fold()
                    return
                else:
                    # raise
                    pyautogui.moveTo(POSITION_BUTTON_ADD_RAISE[0], POSITION_BUTTON_ADD_RAISE[1], duration=0.2)
                    if self.cal > 0.0:
                        pyautogui.click()
                    else:
                        raise_bb = eval('random.randint{}'.format(self.val))
                        pyautogui.click(clicks=raise_bb, interval=0.3)
                    time.sleep(1)
                    pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                                     POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                                     duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
                    pyautogui.click()
            else:
                pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                                 POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                                 duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
                pyautogui.click()

    @staticmethod
    def allin():
        pyautogui.moveTo(POSITION_BUTTON_ADD_RAISE[0], POSITION_BUTTON_ADD_RAISE[1], duration=0.2)
        pyautogui.click(clicks=10, interval=0.3)
        time.sleep(1)
        pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                         POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()
