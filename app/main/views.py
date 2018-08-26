from flask import session, flash, redirect, url_for, render_template, current_app
from .forms import NameForm
from ..models import User
from .. import db
from ..mail import send_mail
from datetime import datetime
from . import main


@main.route('/', methods=['get', 'post'])
def index():
    # form = NameForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.name.data).first()
    #     if not user:
    #         new_user = User(username=form.name.data)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         # session['known'] = False
    #         result = send_mail(current_app.config['MAIL_ADMIN'], 'new user registered', 'mail/registry', user=new_user)
    #         if result:
    #             flash('邮件已发送！')
    #         else:
    #             flash('邮件发送失败！')
    #     else:
    #         session['known'] = True
    #     session['name'] = form.name.data
    #     return redirect(url_for('main.index'))
    return render_template("index.html", current_time=datetime.utcnow())


@main.route('/<name>')
def hello_world(name):
    session['name'] = name
    return render_template("user.html", name=name)
