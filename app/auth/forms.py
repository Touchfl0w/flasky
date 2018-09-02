from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), ])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistForm(FlaskForm):
    email = StringField('邮箱',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('用户名', validators=[DataRequired(
        message='用户名不能为空'),Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0,message='用户名必须为字母数字下划线点组成')])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo(
        'password2', message='两次密码必须相同.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件已注册.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已注册.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo(
        'password2', message='两次密码必须相同')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('密保邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    submit = SubmitField('发送')


class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo(
        'password2', message='两次密码必须相同')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')