from flask import render_template
from flask_login import login_required
from app.decorators import permission_required, admin_required
from ..models import Permission
from datetime import datetime
from . import main


@main.route('/', methods=['get', 'post'])
def index():
    return render_template("index.html", current_time=datetime.utcnow())


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

