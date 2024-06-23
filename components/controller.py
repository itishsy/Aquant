from datetime import datetime, timedelta
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
        eng.strategy = name
        if act == 'search' or act == 'all':
            print('engine', name, 'action: search, start...')
            eng.do_search()
            print('engine', name, 'action: search, done!')
        if act == 'watch' or act == 'all':
            print('engine', name, 'action: watch, start...')
            eng.do_watch()
            print('engine', name, 'action: watch, done!')
    comp.status = Component.Status.READY
    comp.run_end = datetime.now()
    comp.save()


def init_engine():
    init_time = datetime(datetime.year, 1, 1)
    if not Component.select(Component.name == 'fetcher').exists():
        Component.create(name='fetcher', clock_time=datetime.now(), run_start=init_time, run_end=init_time,
                         status=Component.Status.READY)
    else:
        Component.update(clock_time=datetime.now(), status=Component.Status.READY).where(
            Component.name == 'fetcher').execute()
    Component.delete().where(Component.name != 'fetcher').execute()
    for name in engine.strategy:
        Component.create(name=name.lower()[0] + name[1:], clock_time=datetime.now(), run_start=init_time,
                         run_end=init_time, status=Component.Status.READY)


if __name__ == '__main__':
    init_engine()
