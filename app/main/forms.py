from flask_pagedown.fields import PageDownField
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, ValidationError, Email, Regexp

from app.models import User, Role


class NameForm(FlaskForm):
    name = StringField(' 姓名', validators=[DataRequired()])
    submit = SubmitField('提交！')


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[DataRequired(), Length(1, 10)])
    location = StringField('地点', validators=[DataRequired(), Length(1, 60)])
    about_me = TextAreaField('个人简述(不超过120字）', validators=[DataRequired(), Length(1, 120)])
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(
        message='用户名不能为空'), Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0, message='用户名必须为字母数字下划线点组成')])
    confirmed = BooleanField('账户已确认')
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=[DataRequired(), Length(1, 10)])
    location = StringField('地点', validators=[DataRequired(), Length(1, 60)])
    about_me = TextAreaField('个人简述(不超过120字）', validators=[DataRequired(), Length(1, 120)])
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user
        map = {
            'administrator': '管理员',
            'user': '普通用户',
            'moderator': '协管员',
        }
        self.role.choices = [(role.id, map[role.name]) for role in Role.query.order_by(Role.name).all()]

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(eamil=field.data).first():
            raise ValidationError('该邮件已注册')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('该用户名已注册')


class PostForm(FlaskForm):
    submit = SubmitField('提交')
    body = PageDownField('写下你的想法吧', validators=[DataRequired()])


