from datetime import datetime
from models.component import Component
import candles.fetcher as fet
from engines import *


def start_component(name, act):
    comp = Component.get(Component.name == name)
    comp.status = Component.Status.RUNNING
    comp.run_start = datetime.now()
    comp.save()
    if act == 'fetch':
        fet.fetch_all()
    else:
        eng = engine.strategy[name.capitalize()]()
        if act == 'search':
            eng.do_search()
        elif act == 'watch':
            eng.do_watch()
    comp.status = Component.Status.READY
    comp.run_end = datetime.now()
    comp.save()


if __name__ == '__main__':
    start_component()
