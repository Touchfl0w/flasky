from random import randint

from faker import Faker
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import User, Post


def users(count=100):
    fake = Faker()
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        try:
            db.session.commit()
            i = i+1
        except IntegrityError:
            db.session.rollback()


def posts(count=100):
    fake = Faker()
    i = 0
    user_count = User.query.count()
    while i < count:
        u = User.query.offset(randint(0,user_count-1)).first()
        post = Post(body=fake.text(),
                    timestamp=fake.past_date(),
                    author=u)
        db.session.add(post)
        i = i + 1
    db.session.commit()
