import unittest
from random import randint

from app import db
from app.models import User

class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = User(password='cat')
        self.assertTrue(u.password_hash is not None)

    def test_password_getter(self):
        u = User(password = 'dog')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):
        u = User(password='dog')
        self.assertTrue(u.verify_password('dog'))
        self.assertFalse(u.verify_password('cat'))

    def test_salt_random(self):
        u = User(password='dog')
        u1 = User(password='dog')
        self.assertTrue(u.password_hash != u1.password_hash)

    def test_avatar_hash_upgrade(self):
        u = User(email=str(randint(1000, 10000)))
        hash0 = u.avatar_hash
        u.change_email(str(randint(1000, 10000)))
        # change_email仅仅db.session.add
        hash1 = u.avatar_hash
        self.assertTrue(hash0 != hash1)


