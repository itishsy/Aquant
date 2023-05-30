from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField,IntegerField, PasswordField, SelectField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo


class NotifyForm(FlaskForm):
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    strategy = SelectField('策略', choices=[('DRC', '反转确认'), ('GAR', '金叉调整'), ('MAR', '趋势调整')],
                              validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    dt = StringField('发生时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    status = IntegerField('发送状态', default=0)
    submit = SubmitField('提交')


class SignalForm(FlaskForm):
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    dt = StringField('时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    freq = StringField('级别', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    strategy = StringField('策略', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    value = StringField('策略值', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    tick = BooleanField('转票据', default=False)
    submit = SubmitField('提交')


class TicketForm(FlaskForm):
    code = StringField('编码', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    dt = StringField('时间', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    freq = StringField('级别', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    strategy = StringField('策略', validators=[DataRequired(message='不能为空'), Length(0, 64, message='长度不正确')])
    submit = SubmitField('提交')