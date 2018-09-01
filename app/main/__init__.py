from flask import Blueprint

from app.models import Permission

main = Blueprint('main', __name__)


# 把Permission类导入模板，在蓝图__init__文件中定义，导入时会自动执行!
@main.app_context_processor
def inject_permission():
    return dict(Permission=Permission)


from . import views, errors