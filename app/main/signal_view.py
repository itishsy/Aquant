from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.signal import Signal
from models.ticket import Ticket
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length

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
            elif action == 'tick':
                status = request.args.get('status')
                sig.tick = (status == '1')
                sig.updated = datetime.now()
                sig.save()
                Ticket.create(code=sig.code, status=status)
            flash('操作成功')
        except:
            flash('操作失败')

    # 查询列表
    query = Signal.select().where(Signal.status == 1).order_by(Signal.tick.desc())
    total_count = query.select().where(Signal.status == 1).count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('signallist.html', form=dict, current_user=current_user)


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
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    dt = StringField('时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    freq = StringField('级别', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    strategy = StringField('策略', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    submit = SubmitField('提交')
