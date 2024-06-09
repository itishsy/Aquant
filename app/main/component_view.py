from flask import render_template, flash, redirect, url_for
from flask_login import login_required, current_user
from . import main
from models.component import Component
from components.controller import start_component
from threading import Thread
from app import utils


@main.route('/component', methods=['GET'])
@login_required
def component():
    cos = Component.select()
    dic = {'fetcher': '未知', 'searcher': '未知', 'watcher': '未知', 'sender': '未知', 'fetcher_time': '未知', 'searcher_time': '未知', 'watcher_time': '未知', 'sender_time': '未知'}
    for co in cos:
        if co.status == 0:
            dic[co.name] = '未启动'
        elif co.status == 1:
            dic[co.name] = '已启动'
        elif co.status == 2:
            dic[co.name] = '运行中'
        dic["{}_time".format(co.name)] = co.run_end
    return render_template('component.html', dic=dic, current_user=current_user)


@main.route('/componentlist', methods=['GET', 'POST'])
@login_required
def componentlist():
    query = Component.select()
    dic = {'content': utils.query_to_list(query)}
    return render_template('componentlist.html', form=dic)


@main.route('/fetch', methods=['GET'])
@login_required
def fetch():
    th = Thread(target=start_component, args=('fetcher', 'fetch'))
    # th.daemon = True
    th.start()
    return redirect(url_for('main.componentlist'))


@main.route('/search', methods=['GET'])
@login_required
def search(eng):
    th = Thread(target=start_component, args=(eng, 'search'))
    # th.daemon = True
    th.start()
    return redirect(url_for('main.componentlist'))


@main.route('/watch', methods=['GET'])
@login_required
def watch(eng):
    th = Thread(target=start_component, args=(eng, 'watch'))
    # th.daemon = True
    th.start()
    return redirect(url_for('main.componentlist'))
