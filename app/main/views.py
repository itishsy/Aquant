from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.signal import Signal
from models.ticket import Ticket
from models.trade import Trade
from models.choice import Choice
from datetime import datetime
from candles.storage import find_candles
from common.utils import now_ymd
from datetime import timedelta

logger = get_logger(__name__)
cfg = get_config()


# 通用列表查询
def common_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 删除操作
    if action == 'del' and id:
        try:
            DynamicModel.get(DynamicModel.id == id).delete_instance()
            flash('删除成功')
        except:
            flash('删除失败')

    # 查询列表
    query = DynamicModel.select()
    total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template(view, form=dict, current_user=current_user)


# 通用单模型查询&新增&修改
def common_edit(DynamicModel, form, view):
    id = request.args.get('id', '')
    if id:
        # 查询
        model = DynamicModel.get(DynamicModel.id == id)
        if request.method == 'GET':
            utils.model_to_form(model, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, model)
                model.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = DynamicModel()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


# 根目录跳转
@main.route('/', methods=['GET'])
@login_required
def root():
    return redirect(url_for('main.index'))


# 首页
@main.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', current_user=current_user)


# 根目录跳转
@main.route('/api/stats/summary', methods=['GET'])
@login_required
def summary():

    # choice
    c_size = Choice.select().where(Choice.status.in_([Choice.Status.WATCH])).count()
    today = now_ymd()
    if today.weekday() == 5:
        today = today - timedelta(days=1)
    elif today.weekday() == 6:
        today = today - timedelta(days=2)
    c_today_size = Choice.select().where(Choice.created >= today).count()

    # buy point
    b_size = Choice.select().where(Choice.status == Choice.Status.DEAL).count()     # Ticket.select().where(Ticket.status < Ticket.Status.DONE).count()
    b_today_size = Choice.select().where(Choice.status == Choice.Status.DEAL, Choice.created >= today).count()     # Ticket.select().where(Ticket.created >= today).count()

    # out
    o_size = Choice.select().where(Choice.status.in_([Choice.Status.DISUSE, Choice.Status.DONE])).count()
    o_today_size = Choice.select().where(Choice.status.in_([Choice.Status.DISUSE, Choice.Status.DONE]), Choice.created >= today).count()

    recently = datetime.now() - timedelta(days=10)
    s_size = Signal.select().where(Signal.created > recently).count()
    s_today_size = Signal.select().where(Signal.created > today).count()

    data = {'c_size': c_size,
            'c_today_size': c_today_size,
            'b_size': b_size,
            'b_today_size': b_today_size,
            'o_size': o_size,
            'o_today_size': o_today_size,
            's_size': s_size,
            's_today_size': s_today_size}
    return jsonify(data)


@main.route('/api/get/id', methods=['GET'])
@login_required
def getTickIdByCode():
    code = request.args.get('code')
    data = {'id': -1}
    if Ticket.select().where(Ticket.code == code).exists():
        tic = Ticket.get(Ticket.code == code)
        data = {'id':  tic.id}
    return jsonify(data)

# 根目录跳转
@main.route('/api/save/ticket', methods=['POST'])
@login_required
def save_ticket():
    id = request.args.get('id')
    status = request.args.get('status')
    sig = Signal.get_by_id(id)
    if sig is None:
        flash('操作失败：id={}不存在'.format(id))
    else:
        sig.watch = status
        sig.save()
        Ticket.create(code=sig.code, status=0)
        flash('操作成功')
    data = {'ok': 1}
    return jsonify(data)
