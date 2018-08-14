from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from forms import NameForm
from flask_sqlalchemy import SQLAlchemy
import os
from flask_migrate import Migrate
from sqlalchemy import MetaData
from flask_mail import Mail, Message

app = Flask(__name__)

app.config['SECRET_KEY'] = 'hello flasky'
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////'+ os.path.join(base_dir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
print(os.environ.get('MAIL_PASSWORD'))
app.config['MAIL_SUBJECT_PREFIX'] = 'FLASKY'
app.config['MAIL_SENDER'] = '就爱深蓝色 <1754643407@qq.com>'
app.config['MAIL_ADMIN'] = os.environ.get('MAIL_ADMIN')
naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app=app,metadata=MetaData(naming_convention=naming_convention))
migrate = Migrate(app,db,render_as_batch=True)

def send_mail(to,subject,template,**kargs):
    rel = True
    msg = Message(app.config['MAIL_SUBJECT_PREFIX']+subject,sender=app.config['MAIL_SENDER'],recipients=[to])
    msg.body = render_template(template + '.txt',**kargs)
    msg.html = render_template(template + '.html',**kargs)
    try:
        mail.send(msg)
    except:
        rel = False
    finally:
        return rel


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(64),unique=True)
    users = db.relationship('User',backref='role',lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String,unique=True)
    role_id = db.Column(db.Integer,db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User {}>'.format(self.username)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db,User=User,Role=Role)


@app.route('/', methods=['get', 'post'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if not user:
            new_user = User(username=form.name.data)
            db.session.add(new_user)
            db.session.commit()
            session['known'] = False
            text = app.config['MAIL_ADMIN']
            # if text:
            send_mail(app.config['MAIL_ADMIN'], 'new user registried', 'mail/registry', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('index'))

    return render_template("index.html", current_time=datetime.utcnow(), form=form, name=session.get(
        'name'),known=session.get('known'))


@app.route('/<name>')
def hello_world(name):
    session['name'] = name
    return render_template("user.html", name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500

if __name__ == '__main__':
    #用manager接管app启动后，不要传任何参数
    app.run(debug=True)
