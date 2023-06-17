from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.choice import Choice
from models.ticket import Ticket
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length
from storage.dba import get_symbol, find_candles
from common.dicts import choice_strategy

logger = get_logger(__name__)
cfg = get_config()


@main.route('/choice_list', methods=['GET', 'POST'])
@login_required
def choice_list():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 查询列表
    today = request.args.get('today')
    if today:
        last_day = find_candles('000001', 101, limit=1)[0].dt
        query = Choice.select().where(Choice.status == 1, Choice.created >= last_day)
        total_count = query.select().where(Choice.status == 1, Choice.created >= last_day).count()
    else:
        query = Choice.select().where(Choice.status == 1).order_by(Choice.dt.desc(), Choice.created.desc())
        total_count = Choice.select().where(Choice.status == 1).count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('choicelist.html', form=dict, current_user=current_user)


@main.route('/choice_edit', methods=['GET', 'POST'])
@login_required
def choice_edit():
    id = request.args.get('id', '')
    form = ChoiceForm()
    if id:
        # 查询
        chi = Choice.get(Choice.id == id)
        if request.method == 'GET':
            utils.model_to_form(chi, form)
        # 修改
        if request.method == 'POST':
            action = request.args.get('action')
            if action == 'del':
                chi.status = 0
                chi.updated = datetime.now()
                chi.save()
            elif action == 'tick':
                chi.updated = datetime.now()
                chi.save()
                if not Ticket.select().where(Ticket.code == chi.code).exists():
                    Ticket.create(code=chi.code, name=chi.name, status=1, created=datetime.now())
                    flash('操作成功。新建票据')
                else:
                    tic = Ticket.get(Ticket.code == chi.code)
                    if tic.status == 0:
                        tic.status = 1
                        tic.updated = datetime.now()
                        tic.save()
                        flash('票据已存在，已重新生效')
                    else:
                        flash('票据已存在且有效')
            elif form.validate_on_submit():
                utils.form_to_model(form, chi)
                chi.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = Choice()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template('chiceedit.html', form=form, current_user=current_user)


@main.route('/load_choice', methods=['GET'])
@login_required
def load_choice():
    code = request.args.get('code', '')
    data = {'id': -1}
    if code:
        if Choice.select().where(Choice.code == code).exists():
            data = Choice.get(Choice.code == code)
        else:
            sym = get_symbol(code)
            if sym is not None:
                data = {'id': 0,
                        'code': code,
                        'name': sym.name,
                        'freq': 30,
                        'dt': datetime.now().strftime('%Y-%m-%d'),
                        'strategy': 'hot',
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
    value = StringField('策略值', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    submit = SubmitField('提交')
