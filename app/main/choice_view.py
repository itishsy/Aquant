from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.choice import Choice
from models.signal import Signal
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length
from candles.storage import find_candles
from models.symbol import Symbol
from common.dicts import choice_strategy, choice_source, freq_level
from common.utils import now_ymd

logger = get_logger(__name__)
cfg = get_config()


@main.route('/choice_list', methods=['GET', 'POST'])
@login_required
def choice_list():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 查询列表
    today = request.args.get('today')
    status = request.args.get('status')
    if today and today != 'None':
        last_day = now_ymd()  # find_candles('000001', 101, limit=1)[0].dt
        if status:
            query = Choice.select().where(Choice.created >= last_day, Choice.status == status)
        else:
            query = Choice.select().where(Choice.created >= last_day)
        total_count = query.count()
    else:
        if status:
            query = Choice.select().where(Choice.status == status).order_by(
                Choice.created.desc())
        else:
            query = Choice.select().where(Choice.status.in_([Choice.Status.WATCH, Choice.Status.DEAL])).order_by(Choice.created.desc())
        total_count = query.count()

    # 处理分页
    if page:
        query = query.paginate(page, length)

    lis = {'content': utils.query_to_list(query), 'total_count': total_count,
           'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('choicelist.html', form=lis, today=today, current_user=current_user)


@main.route('/choice_edit', methods=['GET', 'POST'])
@login_required
def choice_edit():
    id = request.args.get('id', '')
    form = ChoiceForm()
    if id:
        cho = Choice.get(Choice.id == id)
        action = request.args.get('action')
        if action == 'disuse':
            cho.status = Choice.Status.DISUSE
            cho.updated = datetime.now()
            cho.save()
            flash('操作成功')
        if action == 'deal':
            cho.status = Choice.Status.DEAL
            cho.updated = datetime.now()
            cho.save()
            flash('操作成功')
            """ 
            if not Ticket.select().where(Ticket.code == cho.code).exists():
                tic = Ticket()
                tic.add_by_choice(cho)
                flash('操作成功')
            else:
                tic = Ticket.get(Ticket.code == cho.code)
                flash('操作成功')
                return redirect(url_for('main.ticket_edit', id=tic.id))
            """
        # 查询
        if request.method == 'GET':
            cs = Signal.get(id=cho.cid)
            bs, ss, os = None, None, None
            if cho.bid:
                bs = Signal.get(id=cho.bid)
            if cho.sid:
                ss = Signal.get(id=cho.sid)
            if cho.oid:
                os = Signal.get(id=cho.oid)
            return render_template('choicedetail.html', choice=cho, cs=cs, bs=bs, ss=ss, os=os, current_user=current_user)

            # utils.model_to_form(cho, form)
            # if Ticket.select().where(Ticket.code == cho.code).exists():
            #     tic = Ticket.get(Ticket.code == cho.code)
            #     form.__setattr__('tid', tic.id)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, cho)
                cho.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = Choice()
            utils.form_to_model(form, model)
            model.save()
            chi = Choice.get(Choice.code == model.code)
            return redirect(url_for('main.choice_edit', id=chi.id))
        else:
            utils.flash_errors(form)
    return render_template('choiceedit.html', form=form, current_user=current_user)


@main.route('/api/load_choice', methods=['GET'])
@login_required
def load_choice():
    code = request.args.get('code', '')
    data = {'id': -1}
    if code:
        if Choice.select().where(Choice.code == code).exists():
            chi = Choice.get(Choice.code == code)
            data = chi.__data__
        else:
            sym = Symbol.get(Symbol.code == code)
            if sym is not None:
                data = {'id': 0,
                        'code': code,
                        'name': sym.name,
                        'freq': 30,
                        'dt': datetime.now().strftime('%Y-%m-%d'),
                        'strategy': 'HOT',
                        'status': 1
                        }
    return jsonify(data)


class ChoiceForm(FlaskForm):
    id = IntegerField('id')
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    name = StringField('名称', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    dt = StringField('发出时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    freq = StringField('级别', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    strategy = SelectField('策略', choices=choice_strategy(), default='hot')
    source = SelectField('來源', choices=choice_source(), default='MANUAL')
    submit = SubmitField('提交')
