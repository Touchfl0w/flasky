from app import create_app, db
from app.models import User, Role
from flask_migrate import Migrate

app = create_app('default')
migrate = Migrate(app, db, render_as_batch=True)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, User=User, Role=Role)


if __name__ == '__main__':
    #用manager接管app启动后，不要传任何参数
    app.run(debug=True)
