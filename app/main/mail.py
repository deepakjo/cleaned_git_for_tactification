from functools import wraps
from threading import Thread
from flask import current_app, render_template
from flask_mail import Mail, Message
from .. import mail
from time import time

def clock(func):
    @wraps(func)
    def duration(**kwargs):
        t0 = time()
        func(**kwargs)
        elapsed_time = time() - t0
        print 'elapsed time to send mail is ', elapsed_time
        return
    return duration

@clock
def send_async_email(**kwargs):
    with kwargs['app'].app_context():
        mail.send(kwargs['msg'])

""" This function is to send mail.
    mail is provided by __init__ and context from current_app
"""
def send_email(to, subject, template, **kwargs):
    app = current_app._get_current_object()
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    kwargs = {'app': app, 'msg':msg}
    send_async_email(**kwargs)
    return
