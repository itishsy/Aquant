from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.ticket import Ticket
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length
from common.utils import freq_level

logger = get_logger(__name__)
cfg = get_config()


@main.route('/ticketlist', methods=['GET', 'POST'])
@login_required
def ticketlist():
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    if id:
        tic = Ticket.get(Ticket.id == id)
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
    query = Ticket.select().where(Ticket.status < 3).order_by(Ticket.hold.desc(),Ticket.buy)
    total_count = query.select().where(Ticket.status < 3).count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('ticketlist.html', form=dict, fel=freq_level, current_user=current_user)


@main.route('/ticketedit', methods=['GET', 'POST'])
@login_required
def ticketedit():
    id = request.args.get('id', '')
    form = TicketForm()
    if id:
        # 查询
        model = Ticket.get(Ticket.id == id)
        if request.method == 'GET':
            utils.model_to_form(model, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, model)
                model.updated = datetime.now()
                model.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = Ticket()
            utils.form_to_model(form, model)
            model.created = datetime.now()
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template('ticketedit.html', form=form, current_user=current_user)


class TicketForm(FlaskForm):
    name = StringField('名称', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    cost = DecimalField('成本')
    hold = IntegerField('持有量')
    buy = SelectField('买入级别', choices=freq_level())
    sell = SelectField('卖出级别', choices=freq_level())
    cut = DecimalField('止损点', validators=[DataRequired(message='不能为空')])
    clean = SelectField('剔除级别', choices=freq_level())
    status = SelectField('状态', choices=[(0, '观察中'), (1, '持有'), (2, '清仓'), (3, '弃用')])
    source = SelectField('来源于', choices=[('TTS', '趋势策略'), ('自选', '自选')])
    created = StringField('创建时间')
    submit = SubmitField('提交')
