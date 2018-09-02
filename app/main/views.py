from flask import render_template, redirect, flash, url_for
from flask_login import login_required, current_user

from app import db
from app.decorators import permission_required, admin_required
from .forms import EditProfileForm, EditProfileAdminForm
from ..models import Permission, User, Role
from datetime import datetime
from . import main


@main.route('/', methods=['get', 'post'])
def index():
    return render_template("index.html", current_time=datetime.utcnow())


@main.route('/user/<username>')
@login_required
def user(username):
    """用户资料页"""
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


@main.route('/edit_profile', methods=['GET', "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        db.session.commit()
        flash('您的个人信息已保存')
        return redirect(url_for('main.user', username=current_user.username))
    form.name = current_user.name
    form.location = current_user.location
    form.about_me = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
# 千万注意，url_for的endpoint参数是试图函数名，不是url链接名，虽然一般情况下是相同的！！
def edit_profile_admin(id):
    user = User.query.filter_by(id=id).first()
    form = EditProfileAdminForm(user)
    if form.validate_on_submit():
        user.change_email(form.email.data)
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash('用户资料已修改')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/admin')
@login_required
@admin_required
def for_admin():
    return 'for admin'


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENT)
def for_moderate():
    return 'for moderate'

