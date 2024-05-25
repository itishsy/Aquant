from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.signal import Signal
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length
from common.dicts import trade_type, single_source
from common.utils import now_ymd

logger = get_logger(__name__)
cfg = get_config()


@main.route('/signallist', methods=['GET', 'POST'])
@login_required
def signallist():
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    if id:
        sig = Signal.get(Signal.id == id)
        try:
            # 删除操作
            if action == 'del':
                sig.status = 0
                sig.updated = datetime.now()
                sig.save()
            # elif action == 'tick':
            #     sig.tick = True
            #     sig.updated = datetime.now()
            #     sig.save()
            #     if not Ticket.select().where(Ticket.code == sig.code).exists():
            #         Ticket.create(code=sig.code, name=sig.name, status=0, created=datetime.now())
            # elif action == 'untick':
            #     sig.tick = False
            #     sig.updated = datetime.now()
            #     sig.save()
        except:
            flash('操作失败')

    # 查询列表
    today = request.args.get('today')
    if today and today != 'None':
        last_day = now_ymd()  # find_candles('000001', 101, limit=1)[0].dt
        query = Signal.select().where(Signal.created >= last_day).order_by(Signal.created.desc())
        total_count = query.count()
    else:
        query = Signal.select().order_by(Signal.created.desc()).limit(180)
        total_count = query.count()

    cdt = datetime(datetime.now().year,datetime.now().month,datetime.now().day)

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('signallist.html', form=dict, cdt=cdt, today=today, current_user=current_user)


@main.route('/signaledit', methods=['GET', 'POST'])
@login_required
def signaledit():
    id = request.args.get('id', '')
    form = SignalForm()
    if id:
        # 查询
        model = Signal.get(Signal.id == id)
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
            model = Signal()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template('signaledit.html', form=form, current_user=current_user)


class SignalForm(FlaskForm):
    id = IntegerField('id')
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    name = StringField('名称', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    type = SelectField('信号', choices=trade_type())
    dt = StringField('发出时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    freq = StringField('级别', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    source = SelectField('信号源', choices=single_source())
    submit = SubmitField('提交')
