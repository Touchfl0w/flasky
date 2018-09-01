import os

base_dir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hello flasky'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_ADMIN = os.environ.get('MAIL_ADMIN')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_SUBJECT_PREFIX = 'FLASKY'
    MAIL_SENDER = '就爱深蓝色 <1754643407@qq.com>'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEVELOPMENT_DATABASE_URI') or 'sqlite:////'+ os.path.join(
        base_dir,'data.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TESTING_DATABASE_URI') or 'sqlite://'


class ProductConfig(Config):
    PRODUCTION = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('PRODUCT_DATABASE_URI') or 'sqlite:////' + os.path.join(
        base_dir, 'data_pro.sqlite')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductConfig,
    'default': DevelopmentConfig
}