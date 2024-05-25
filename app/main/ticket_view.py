from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify, redirect, url_for
from flask_login import login_required, current_user
from app import utils
from . import main
from models.ticket import Ticket
from models.signal import Signal
from models.trade import Trade
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length
from common.dicts import freq_level, choice_strategy, trade_strategy, buy_type
from candles.storage import find_candles
from common.utils import now_ymd
from models.symbol import Symbol

logger = get_logger(__name__)
cfg = get_config()


@main.route('/ticket_list', methods=['GET', 'POST'])
@login_required
def ticket_list():
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    if id:
        tic = Ticket.get(Ticket.code == id)
        try:
            # 删除操作
            if action == 'del':
                tic.status = 3
                tic.updated = datetime.now()
                tic.save()
                flash('操作成功')
        except:
            flash('操作失败')

    # 查询列表
    today = request.args.get('today')
    sea = request.args.get('sea')
    if today and today != 'None':
        last_day = now_ymd()  # find_candles('000001', 101, limit=1)[0].dt
        query = Ticket.select().where(Ticket.status < 3, Ticket.created > last_day).order_by(Ticket.hold.desc())
        total_count = query.count()
    elif sea and sea != 'None':
        query = Ticket.select().where((Ticket.code.contains(sea)) | (Ticket.name.contains(sea)))
        total_count = query.count()
    else:
        query = Ticket.select().where(Ticket.status < 3).order_by(Ticket.status.desc(), Ticket.hold.desc())
        total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('ticketlist.html', form=dict, today=today)


@main.route('/ticket_edit', methods=['GET', 'POST'])
@login_required
def ticket_edit():
    id = request.args.get('id', '')
    form = TicketForm()
    if id:
        # 查询
        tic = Ticket.get(Ticket.id == id)
        action = request.args.get('action')
        if action == 'del':
            tic.status = 4
            tic.updated = datetime.now()
            tic.save()
            flash('票据已弃用')

        if request.method == 'GET':
            utils.model_to_form(tic, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, tic)
                tic.id = id
                tic.updated = datetime.now()
                tic.save()
                return redirect(url_for('main.ticket_detail', id=tic.id))
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = Ticket()
            utils.form_to_model(form, model)
            model.created = datetime.now()
            model.save()
            return redirect(url_for('main.ticket_detail', id=model.id))
        else:
            utils.flash_errors(form)
    return render_template('ticketedit.html', form=form, current_user=current_user)


@main.route('/ticket_detail', methods=['GET', 'POST'])
@login_required
def ticket_detail():
    id = request.args.get('id', '')
    ticket = None
    form = TicketForm()
    trades = []
    singles = []
    if id:
        # 查询
        if Ticket.select().where(Ticket.code == id).exists():
            ticket = Ticket.get(Ticket.code == id)
        else:
            ticket = Ticket.get(Ticket.id == id)
        action = request.args.get('action')
        if action == 'wat':
            ticket.status = 0
            ticket.watch = 0
            ticket.updated = datetime.now()
            ticket.save()
            flash('票据已调为观察')
        if action == 'tob':
            ticket.status = 1
            ticket.watch = 1
            ticket.updated = datetime.now()
            ticket.save()
            flash('票据已调为盯盘')
        if action == 'trd':
            t = request.args.get('type', '')
            if t == 'kai' and not Signal.select().where(Signal.code == ticket.code).exists():
                flash('未产生任何信号，无法交易')
            if (t == 'jia' or t == 'pin') and ticket.hold < 100:
                flash('持有量不足，无法交易')

            sis = Signal.select().where(Signal.code == ticket.code, Signal.status == 1).order_by(
                Signal.dt.desc()).limit(1)
            if len(sis) > 0:
                si = sis[-1]
            else:
                si = Signal()
                si.code = ticket.code
                si.name = ticket.name
                si.freq = 1
                si.price = 1
            tr = Trade()
            tr.code = si.code
            tr.name = si.name
            tr.dt = datetime.now().strftime('%Y-%m-%d')
            tr.freq = si.freq
            tr.price = si.price
            tr.volume = 100
            tr.status = 1
            tr.fee = 5
            tr.created = datetime.now()
            if t == 'kai':
                tr.type = 0
                tr.comment = '开仓'
            elif t == 'jia':
                tr.type = 0
                tr.comment = '加仓'
            elif t == 'jin':
                tr.type = 1
                tr.comment = '减仓'
                tr.volume = ticket.hold
            else:
                tr.type = 1
                tr.comment = '平仓'
                tr.volume = ticket.hold
            tr.save()
            tr1 = Trade.select().where(Trade.code == si.code).order_by(Trade.id.desc()).first()
            return redirect(url_for('main.tradeedit', id=tr1.id))

        if request.method == 'GET':
            utils.model_to_form(ticket, form)
            ticket.status_text = Ticket.Status.get(ticket.status)
            s_query = Signal.select().where(Signal.code == ticket.code).order_by(Signal.dt.desc()).limit(5)
            t_query = Trade.select().where(Trade.code == ticket.code).order_by(Trade.dt.desc()).limit(5)
            singles = utils.query_to_list(s_query)
            # trades = utils.query_to_list(t_query)
    else:
        flash('参数错误')
    return render_template('ticketdetail.html', ticket=ticket, form=form, singles=singles, trades=trades,
                           current_user=current_user)


@main.route('/api/load_ticket', methods=['GET'])
@login_required
def load_ticket():
    code = request.args.get('code', '')
    data = {'id': -1}
    if code:
        if Ticket.select().where(Ticket.code == code).exists():
            chi = Ticket.get(Ticket.code == code)
            data = chi.__data__
        else:
            sym = Symbol.get(Symbol.code == code)
            if sym is not None:
                data = {'id': 0,
                        'code': code,
                        'name': sym.name,
                        'freq': 30,
                        'dt': datetime.now().strftime('%Y-%m-%d'),
                        'status': 1
                        }
    return jsonify(data)


class TicketForm(FlaskForm):
    id = IntegerField('id')
    name = StringField('名称', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    status = SelectField('状态', choices=Ticket.Status.all())
    strategy = StringField('策略')
    bs_freq = StringField('信號級別')
    bs_dt = StringField('信號時間')
    bs_price = StringField('信號價格')
    bs_strength = StringField('信號强度')
    bp_freq = StringField('買點級別')
    bp_dt = StringField('買點時間')
    bp_price = StringField('買點價格')
    cost = DecimalField('成本')
    hold = IntegerField('持有量')
    created = StringField('创建时间')
    submit = SubmitField('提交')
