
from flask import request, redirect, url_for, flash, render_template, current_app

from app import db, mail
from .forms import LoginForm, RegistForm
from . import auth
from ..models import User
from flask_login import login_user, logout_user, current_user, login_required
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
        mail.send_mail(current_app.config['MAIL_ADMIN'], '用户注册', 'mail/registry', user=user)
        token = user.generate_confirmation_token()
        mail.send_mail(user.email, '确认账户', 'auth/mail/confirm_account', user=user, token=token)
        flash('请前往邮箱确认账户')
        return redirect(url_for('main.index'))
    return render_template('auth/registry.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.verify_token(token):
        db.session.commit()
        flash('账户已经成功确认')
    else:
        flash('账户确认失败，确认链接可能已失效')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if (current_user.is_authenticated) and not (current_user.confirmed) and (
                request.blueprint != 'auth') and (request.endpoint != 'static'):
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/resend_confirmation')
def resend_confirmation():
    email = current_user.email
    token = current_user.generate_confirmation_token()
    mail.send_mail(email, '确认账户', 'auth/mail/confirm_account', user=current_user,
                   token=token)
    flash('账户确认邮件已经重新发送')
    return redirect(url_for('main.index'))