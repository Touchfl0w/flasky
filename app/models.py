from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask_login import UserMixin
from . import login_manager


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role {}>'.format(self.name)


#UserMixin为flask-login插件所必须
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self,password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'confirm': self.id})
        return token

    def verify_token(self, token):
        #这应该是个反序列化器，不用设过期时间，没有盐
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        else:
            if data['confirm'] != self.id:
                return False
        self.confirmed = True
        db.session.add(self)
        return True

    def change_password(self, old_password, new_password):
        if self.verify_password(old_password):
            self.password = new_password
            db.session.add(self)
            db.session.commit()
            return True
        return False

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        token = s.dumps({'confirm': self.id})
        return token

    def _verify_reset_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except Exception:
            return False
        if data['confirm'] != self.id:
            return False
        return True

    def reset_password(self, token, new_password):
        if not self._verify_reset_token(token):
            return False
        self.password = new_password
        db.session.add(self)
        db.session.commit()
        return True

    def __repr__(self):
        return '<User {}>'.format(self.username)

#load_user函数为flask_login必须
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))