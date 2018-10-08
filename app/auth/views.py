
from flask import request, redirect, url_for, flash, render_template, current_app

from app import db, mail
from .forms import LoginForm, RegistForm, ChangePasswordForm, ResetPasswordForm, ResetPasswordRequestForm
from . import auth
from ..models import User
from flask_login import login_user, logout_user, current_user, login_required
from flask import session
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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
    if current_user.is_authenticated:
        current_user.ping()
        # 验证条件待定
        if not (current_user.confirmed) and (
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


@auth.route('/reset_password', methods=['GET', 'POST'])
def reset_password_request():
    """密码忘记时，在登录页重置密码"""
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('未找到该用户')
        token = user.generate_reset_token()
        if not mail.send_mail(user.email, '重置密码', 'auth/mail/reset_password', user=user, token=token):
            flash('邮件发送失败，请联系管理员')
        else:
            flash('密码重置链接已发往您的邮箱')
        return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """邮箱内点击重置密码链接，跳转到此处"""
    form = ResetPasswordForm()
    if form.validate_on_submit():
        s = Serializer(current_app.config['SECRET_KEY'])
        data = s.loads(token)
        user_id = data['confirm']
        user = User.query.filter_by(id = user_id).first()
        if not user.reset_password(token,form.new_password.data):
            flash('链接可能已经失效，请重新发送邮件')
            return redirect(url_for('auth.reset_password_request'))
        flash('密码修改成功，请登录')
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html',form=form)


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """登录后修改自己账户密码"""
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.change_password(form.old_password.data, form.new_password.data):
            flash('您的密码已成功修改，请登录')
            logout_user()
            return redirect(url_for('auth.login'))
        flash('忘记现有密码？请重新输入')
        return redirect(url_for('auth.change_password'))
    return render_template('auth/change_password.html', form=form)
