import unittest

from app.models import Role, User, Permission


class RoleModeTestlCase(unittest.TestCase):
    def test_3roles_inserted(self):
        roles = [role.name for role in Role.query.all()]
        samples = ['user', 'moderator', 'administrator']
        self.assertTrue(samples == roles)

    def test_defaultuser_has_limit_permission(self):
        user = User(username='test', password='123')
        self.assertTrue(not user.can(Permission.MODERATE_COMMENT) and not user.can(Permission.ADMIN))
