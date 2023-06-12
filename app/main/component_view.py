from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import main
from models.component import Component
from strategies.searcher import search_all
from strategies.watcher import watch_all
import asyncio
from threading import Thread,current_thread


@main.route('/component', methods=['GET'])
@login_required
def component():
    cos = Component.select()
    dic = {'fetcher': '未知', 'searcher': '未知', 'watcher': '未知', 'sender': '未知'}
    for co in cos:
        if co.status == 0:
            dic[co.name] = '未启动'
        elif co.status == 1:
            dic[co.name] = '已启动'
        elif co.status == 2:
            dic[co.name] = '运行中'
    return render_template('component.html', dic=dic, current_user=current_user)


@main.route('/searchtask', methods=['GET'])
@login_required
def searchtask():
    th=Thread(target=search_all)
    th.setDaemon(True)
    th.start()
    return redirect(url_for('main.component'))
    #eval('search_all()')
    #asyncio.run(search_task())


@main.route('/watchtask', methods=['GET'])
@login_required
def watchtask():
    th=Thread(target=watch_all)
    th.setDaemon(True)
    th.start()
    return redirect(url_for('main.component'))
    #eval('watch_all()')
    #asyncio.run(watch_task())


async def search_task():
    print("start search task")
    task = asyncio.create_task(search_all())
    await task
    print("search task completed")


async def watch_task():
    print("start watch task")
    task = asyncio.create_task(watch_all())
    await task
    print("watch task completed")