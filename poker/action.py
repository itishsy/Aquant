
class Action:

    def __init__(self, act):
        if act in ['fold', 'call', 'check', 'allin']:
            self.act = act
        elif 'raise' in act:
            self.act = 'raise'
            self.val = eval(act.replace('raise', 'random.randint'))


    def do(self):
        if self.act:
            method = getattr(self, self.act)
            method()

    @staticmethod
    def fold():
        pyautogui.moveTo(POSITION_BUTTON_FOLD[0] + random.randint(1, 10),
                         POSITION_BUTTON_FOLD[1] + random.randint(1, 5),
                         duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒

    @staticmethod
    def check():
        print('todo check')


    @staticmethod
    def call():
        pyautogui.moveTo(POSITION_BUTTON_CALL[0] + random.randint(1, 10),
                         POSITION_BUTTON_CALL[1] + random.randint(1, 5),
                         duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒


    def raise(self):

        pyautogui.moveTo(POSITION_BUTTON_RAISE[0] + random.randint(1, 10),
                         POSITION_BUTTON_RAISE[1] + random.randint(1, 5),
                         duration=0.5)  # duration 参数表示鼠标移动的时间，这里设置为 1 秒

    @staticmethod
    def allin():
        print('todo allin')