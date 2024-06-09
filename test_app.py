from engines import *
from datetime import datetime
from models.user import generate_pwd


def test_search(eng_name):
    eng = engine.strategy[eng_name.capitalize()]()
    eng.strategy = eng_name.capitalize()
    print("[{}] {} start...".format(datetime.now(), eng_name))
    eng.do_search()
    print("[{}] {} end".format(datetime.now(), eng_name))


def test_watch(eng_name):
    eng = engine.strategy[eng_name.capitalize()]()
    eng.strategy = eng_name.capitalize()
    print("[{}] {} start...".format(datetime.now(), eng_name))
    eng.do_watch()
    print("[{}] {} end".format(datetime.now(), eng_name))


def test_model():
    generate_pwd('')
    print('done!')
    # db.connect()
    # db.create_tables([Choice])


if __name__ == '__main__':
    test_watch('u630')
    # test_model()
