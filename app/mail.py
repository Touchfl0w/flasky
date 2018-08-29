from flask import render_template, current_app
from flask_mail import Message
from . import email


def send_mail(to, subject, template, **kargs):
    rel = True
    msg = Message(current_app.config['MAIL_SUBJECT_PREFIX'] + ' ' + subject, sender=current_app.config['MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kargs)
    msg.html = render_template(template + '.html', **kargs)
    try:
        email.send(msg)
    except:
        rel = False
    finally:
        return rel