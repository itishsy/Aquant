import pyautogui
import random
from poker.config import *


class Action:

    def __init__(self, act):
        self.act = None
        if act:
            act = act.strip()
            if act in ['fold', 'call', 'check', 'allin']:
                self.act = act
            elif 'bet' in act:
                self.act = 'bet'
                self.val = eval(act.replace('bet', 'random.randint'))

    def do(self):
        if self.act:
            method = getattr(self, self.act)
            method()
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(100, 150) - 300,
                         duration=0.3)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒

    @staticmethod
    def fold():
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    @staticmethod
    def check():
        print('todo check')

    @staticmethod
    def call():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
        pyautogui.click()

    def bet(self):
        if self.val:
            pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                             POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                             duration=0.2)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒
            pyautogui.click()

    @staticmethod
    def allin():
        print('todo allin')
