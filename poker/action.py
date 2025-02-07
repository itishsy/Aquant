import time

import pyautogui
import random
from poker.config import *


class Action:

    def __init__(self, act):
        self.act = None
        self.val = 0
        if act:
            act = act.strip()
            if act in ['fold', 'call', 'check', 'raise', 'allin']:
                self.act = 'click_{}'.format(act)
            elif 'raise' in act:
                self.act = 'click_raise'
                self.val = int(act.split(':')[1])

    def do(self):
        if self.act:
            if self.val > 0:
                pyautogui.moveTo(POSITION_BUTTON_ADD_RAISE[0], POSITION_BUTTON_ADD_RAISE[1], duration=0.2)
                raise_bb = 10 if self.val > 10 else self.val
                pyautogui.click(clicks=raise_bb, interval=0.3)
                time.sleep(1)
            method = getattr(self, self.act)
            method()
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 100),
                         POSITION_BUTTON_FOLD[1] + random.randint(100, 500) - 800,
                         duration=0.8)  # duration 参数表示鼠标移动的时间

    @staticmethod
    def click_allin():
        pyautogui.moveTo(POSITION_BUTTON_ADD_RAISE[0], POSITION_BUTTON_ADD_RAISE[1], duration=0.2)
        pyautogui.click(clicks=10, interval=0.3)
        time.sleep(1)
        pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                         POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def click_fold():
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def click_check():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def click_call():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def click_raise():
        pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                         POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()