from datetime import datetime

import bleach
from flask import current_app, request
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from . import db
from flask_login import UserMixin, AnonymousUserMixin
from . import login_manager


class Permission:
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE_COMMENT = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self,**kwargs):
        super(Role, self).__init__(**kwargs)
        # 如果父类在对象构造过程中没有接收到permisssions这个参数，则该项默认为None，但最好替换成数字0，与其他权限数字保持一致
        if self.permissions is None:
            self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self,perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permission(self):
        self.permissions = 0

    @staticmethod
    def insert_roles():
        """插入三种角色：user/moderator/administor"""
        roles = {
            'user': [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT],
            'moderator': [Permission.FOLLOW, Permission.WRITE,
                          Permission.COMMENT, Permission.COMMENT, Permission.MODERATE_COMMENT],
            'administrator': [Permission.FOLLOW, Permission.WRITE, Permission.COMMENT, Permission.COMMENT,
                           Permission.MODERATE_COMMENT, Permission.ADMIN],
        }
        default_role = 'user'
        for r_name, r_permissions in roles.items():
            if not Role.query.filter_by(name=r_name).first():
                    role = Role(name=r_name)
                    role.default = (r_name == default_role)
                    role.reset_permission()
                    for perm in r_permissions:
                        role.add_permission(perm)
                    db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role {}>'.format(self.name)


# UserMixin为flask-login插件所必须
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    avatar_hash = db.Column(db.String(32))
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    posts = db.relationship('Post', backref='author', lazy='dynamic')


    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['MAIL_ADMIN']:
                self.role = Role.query.filter_by(name='administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def can(self,perm):
        return self.role.permissions & perm == perm

    def is_administrator(self):
        return self.can(Permission.ADMIN)

    @staticmethod
    def generate_avatar_hash(email):
        import hashlib
        return hashlib.md5(email.encode('utf-8')).hexdigest()

    # @property
    # def email(self):
    #     return self.__email
    #
    # @email.setter
    # def email(self,email):
    #     if self.__email != email:
    #         self.__email = email
    #         self.avatar_hash = User.generate_avatar_hash(email)

    def change_email(self, new_email):
        if self.email != new_email:
            self.email = new_email
            self.avatar_hash = User.generate_avatar_hash(new_email)
            db.session.add(self)
            return True

    def generate_avatar_url(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://secure.gravatar.com/avatar'
        hash = self.avatar_hash or User.generate_avatar_hash(self.email)
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(
            url=url, hash=hash, size=size, default=default, rating=rating)

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
        # 这应该是个反序列化器，不用设过期时间，没有盐
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


class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        return False

    def is_administrator(self):
        return False


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body_html = db.Column(db.Text)
    digest = db.Column(db.Text)

    @staticmethod
    #事件监听函数的具体实现
    def on_change_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code','em', 'i', 'li',
                        'ol', 'pre', 'strong', 'ul','h1', 'h2', 'h3', 'p', 'img']
        #对于带样式/属性的tag,必须添加该字典
        allowed_attrs = {'*': ['class'],
                         'a': ['href', 'rel'],
                         'img': ['src', 'alt']}
        # k = markdown(value, output_format='html')
        #该markdown转换器更简单些,乱码少一些
        import markdown_code_blocks
        k = markdown_code_blocks.highlight(value)
        import re
        digest_list = [i for i in re.findall(r'>(.*?)<', k[:100]) if i]
        target.digest = ''.join(digest_list[:30])
        target.body_html = bleach.clean(k, tags=allowed_tags, attributes=allowed_attrs, strip=True)

    @staticmethod
    def update():
        """更新数据库中ｐｏｓｔｓ表数据，添加ｄｉｇｅｓｔ字段"""
        for post in Post.query.all():
            #第一次增加body_html;有了body_html才能正则出digest
            post.body = post.body
            post.body = post.body
            db.session.add(post)
            db.session.commit()



#注册监听Post.body，一旦有ｓｅｔ事件发生，同时更新Post.body_html
db.event.listen(Post.body, 'set', Post.on_change_body)

login_manager.anonymous_user = AnonymousUser

# load_user函数为flask_login必须
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))