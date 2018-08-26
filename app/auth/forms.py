from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Regexp
from ..models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired(), ])
    remember_me = BooleanField('keep me logged in')
    submit = SubmitField('Log in')

class RegistForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Length(1,64),Email()])
    username = StringField('Username', validators=[DataRequired(
        message='用户名不能为空'),Regexp('^[a-zA-Z][a-zA-Z0-9_.]*$', 0,message='用户名必须为字母数字下划线点组成')])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'password2', message='两次密码必须相同.')])
    password2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮件已注册.')
    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已注册.')