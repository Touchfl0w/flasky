from app import create_app, db
from app.models import User, Role, Post
from flask_migrate import Migrate

app = create_app('development')
migrate = Migrate(app, db, render_as_batch=True)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role,Post=Post)


@app.cli.command()
def test():
    """run unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests') #测试目录名称
    unittest.TextTestRunner(verbosity=2).run(tests)
if __name__ == '__main__':
    #用manager接管app启动后，不要传任何参数
    app.run(debug=True)
