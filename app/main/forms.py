from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField(' 姓名', validators=[DataRequired()])
    submit = SubmitField('提交！')
