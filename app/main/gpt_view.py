from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import utils
from . import main
from models.gpt import Gpt
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.chatgpt.chatanywhere import gpt_4o_api

logger = get_logger(__name__)
cfg = get_config()


@main.route('/gpt_list', methods=['GET', 'POST'])
@login_required
def gpt_list():
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 查询列表
    query = Gpt.select().order_by(Gpt.created.desc())
    total_count = query.count()

    # 处理分页
    if page:
        query = query.paginate(page, length)

    lis = {'content': utils.query_to_list(query), 'total_count': total_count,
           'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template('gptlist.html', form=lis, current_user=current_user)


@main.route('/gpt_edit', methods=['GET', 'POST'])
@login_required
def gpt_edit():
    id = request.args.get('id', '')
    form = GptForm()
    if id:
        gpt = Gpt.get(Gpt.id == id)
        # 查询
        if request.method == 'GET':
            utils.model_to_form(gpt, form)
            return render_template('gptedit.html', form=form, current_user=current_user)
        else:
            # 修改
            utils.form_to_model(form, gpt)
            gpt.save()
            return render_template('gptedit.html', form=form, current_user=current_user)
    else:
        # 新增
        if form.validate_on_submit():
            gpt = Gpt()
            utils.form_to_model(form, gpt)
            gpt.model = 'gpt-4o'
            gpt.created = datetime.now()
            try:
                gpt.content = gpt_4o_api(message=gpt.message)
            except Exception as e:
                gpt.content = e
                gpt.status = 0
            gpt.save()
            return redirect(url_for('main.gpt_edit', id=gpt.id))
        else:
            utils.flash_errors(form)
    return render_template('gptedit.html', form=form, current_user=current_user)


class GptForm(FlaskForm):
    id = IntegerField('id')
    # model = SelectField('模型', choices=choice_model(), default='gpt-4o')
    message = TextAreaField('问题', render_kw={"rows": 3}, validators=[DataRequired(message='不能为空'), Length(0, 500, message='长度不正确')])
    content = TextAreaField('回答', render_kw={"rows": 8})
    submit = SubmitField('提交')
