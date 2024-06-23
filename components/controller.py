from datetime import datetime
from models.component import Component
import candles.fetcher as fet
from engines import *
import time


def start_component(name, act):
    comp = Component.get(Component.name == name)
    comp.status = Component.Status.RUNNING
    comp.run_start = datetime.now()
    comp.save()
    if act == 'fetch':
        fet.fetch_all()
    elif act == 'engine_task':
        start_engine_task()
    elif act == 'engine_init':
        init_engine()
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


def start_engine_task():
    while True:
        for name in engine.strategy:
            st = engine.strategy[name]()
            st.start()
        time.sleep(60 * 5)


def init_engine():
    init_time = datetime(datetime.now().year, 1, 1)
    if not Component.select().where(Component.name == 'fetcher').exists():
        Component.create(name='fetcher', clock_time=datetime.now(), run_start=init_time, run_end=init_time,
                         status=Component.Status.READY).execute()
    else:
        Component.update(clock_time=datetime.now(), status=Component.Status.READY).where(
            Component.name == 'fetcher').execute()
    if not Component.select().where(Component.name == 'engine').exists():
        Component.create(name='engine', clock_time=datetime.now(), run_start=init_time, run_end=init_time,
                         status=Component.Status.READY).execute()
    else:
        Component.update(clock_time=datetime.now(), status=Component.Status.READY).where(
            Component.name == 'engine').execute()
    Component.delete().where(Component.name != 'fetcher').execute()
    for name in engine.strategy:
        Component.create(name=name.lower()[0] + name[1:], clock_time=datetime.now(), run_start=init_time,
                         run_end=init_time, status=Component.Status.READY)


if __name__ == '__main__':
    init_engine()
