from app import get_logger, get_config
import math
from flask import render_template, flash, request, redirect, url_for
from flask_login import login_required, current_user
from app import utils
from . import main
from models.trade import Trade
from models.ticket import Ticket
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length
from common.dicts import trade_type, valid_status, trade_comment

logger = get_logger(__name__)
cfg = get_config()


@main.route('/tradelist', methods=['GET', 'POST'])
@login_required
def tradelist():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 查询列表
    query = Trade.select().order_by(Trade.dt.desc(), Trade.type)
    total_count = query.select().count()

    # 处理分页
    if page: query = query.paginate(page, length)

    list = utils.query_to_list(query)
    for obj in list:
        if obj['created'] > datetime.strptime(datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d"):
            obj['flag'] = 1
        else:
            obj['flag'] = 0

    dict = {'content': list, 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('tradelist.html', form=dict, current_user=current_user)


@main.route('/tradeedit', methods=['GET', 'POST'])
@login_required
def tradeedit():
    id = request.args.get('id', '')
    form = TradeForm()
    if id:
        # 查询
        trade = Trade.get(Trade.id == id)
        if request.method == 'GET':
            utils.model_to_form(trade, form)

        action = request.args.get('action')
        if action == 'del':
            ticket = Ticket.get(Ticket.code == trade.code)
            Trade.delete().where(Trade.id == id).execute()
            return redirect(url_for('main.ticket_detail', id=ticket.id))
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, trade)
                trade.id = id
                trade.save()
                ticket = Ticket.get(Ticket.code == trade.code)
                if trade.type == '0':
                    ticket.hold = ticket.hold + trade.volume
                else:
                    ticket.hold = ticket.hold - trade.volume
                if ticket.hold < 100:
                    ticket.status = 1
                else:
                    ticket.status = 2
                ticket.save()
                return redirect(url_for('main.ticket_detail', id=ticket.id))
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = Trade()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template('tradeedit.html', form=form, current_user=current_user)


class TradeForm(FlaskForm):
    id = IntegerField('id')
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    name = StringField('名称', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    type = SelectField('交易类别', choices=trade_type())
    freq = StringField('交易级别', validators=[DataRequired(message='不能为空')])
    dt = StringField('交易时间', validators=[DataRequired(message='不能为空')])
    price = DecimalField('价格', validators=[DataRequired(message='不能为空')])
    volume = IntegerField('成交量', validators=[DataRequired(message='不能为空')])
    fee = DecimalField('手续费', validators=[DataRequired(message='不能为空')])
    comment = SelectField('说明', choices=trade_comment())
    status = SelectField('状态', choices=valid_status())
    created = StringField('创建时间', validators=[DataRequired(message='不能为空')])
    submit = SubmitField('提交')
