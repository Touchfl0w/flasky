from flask import Flask,render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_script import Manager

app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
manager = Manager(app)

@app.route('/')
def index():
    current_time = datetime.utcnow()
    return render_template("index.html", current_time=current_time)

@app.route('/<name>')
def hello_world(name):
    return render_template("user.html", name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"),500

if __name__ == '__main__':
    #用manager接管app启动后，不要传任何参数
    manager.run()
