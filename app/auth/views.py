
from flask import request, redirect, url_for, flash, render_template

from app import db
from .forms import LoginForm, RegistForm
from . import auth
from ..models import User
from flask_login import login_user, logout_user, current_user
from flask import session

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            a = session
            session['known'] = True
            next = request.args.get('next')
            #next参数是客户端发送来的数据，不可信，必须过滤！防止重定向攻击！
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
        else:
            flash('Invalid Username or Password!')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    #默认退出当前账号
    logout_user()
    flash('您已退出登录！')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET','POST'])
def register():
    form = RegistForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash('用户已注册')
        return redirect(url_for('main.index'))
    return render_template('auth/registry.html', form=form)
