from flask import session, flash, redirect, url_for, render_template, current_app
from .forms import NameForm
from ..models import User
from .. import db
from ..mail import send_mail
from datetime import datetime
from . import main


@main.route('/', methods=['get', 'post'])
def index():
    return render_template("index.html", current_time=datetime.utcnow())


@main.route('/<name>')
def hello_world(name):
    session['name'] = name
    return render_template("user.html", name=name)
