from app import get_logger, get_config
import math
from flask import render_template, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.trade import Trade
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Length

logger = get_logger(__name__)
cfg = get_config()


@main.route('/tradelist', methods=['GET', 'POST'])
@login_required
def tradelist():
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    if id:
        tic = Trade.get(Trade.id == id)
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
    query = Trade.select().order_by(Trade.dt.desc(), Trade.type)
    total_count = query.select().count()

    # 处理分页
    if page: query = query.paginate(page, length)

    list = utils.query_to_list(query)
    for obj in list:
        if obj['created'] > datetime.strptime(datetime.now().strftime("%Y-%m-%d"),"%Y-%m-%d"):
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
        model = Trade.get(Trade.id == id)
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
            model = Trade()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template('tradeedit.html', form=form, current_user=current_user)


class TradeForm(FlaskForm):
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 6, message='长度不正确')])
    freq = StringField('交易级别', validators=[DataRequired(message='不能为空')])
    dt = StringField('交易时间', validators=[DataRequired(message='不能为空')])
    strategy = StringField('交易策略', validators=[DataRequired(message='不能为空')])
    price = DecimalField('价格', validators=[DataRequired(message='不能为空')])
    type = SelectField('类别', choices=[(0, '买入'), (1, '卖出')])
    status = SelectField('状态', choices=[(0, '未成交'), (1, '已成交')])
    notify = SelectField('通知', choices=[('0', '未通知'), ('1', '已通知')])
    created = StringField('创建时间')
    submit = SubmitField('提交')
