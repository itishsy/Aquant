import datetime

work_path = "D:\\PythonProject\\Aquant"
host = "127.0.0.1"
port = 3306
username = "root"
password = "root"
prefix = ['00', '60', '30', '51']


def get_latest(klt):
    now = datetime.datetime.now()
    if klt == 102:
        return now - datetime.timedelta(days=365 * 3)
    elif klt == 101:
        return now - datetime.timedelta(days=365)
    elif klt == 120:
        return now - datetime.timedelta(days=200)
    elif klt == 60:
        return now - datetime.timedelta(days=100)
    elif klt == 30:
        return now - datetime.timedelta(days=50)
    elif klt == 15:
        return now - datetime.timedelta(days=25)
    else:
        return now
