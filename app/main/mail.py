from threading import Thread
from flask import current_app, render_template
from flask_mail import Mail, Message
from .. import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

""" This function is to send mail.
    mail is provided by __init__ and context from current_app
"""
def send_email(to, subject, template, **kwargs):
    print 'to', to
    print current_app.config['MAIL_USERNAME']
    print current_app.config['MAIL_PASSWORD']
    msg = Message(current_app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + subject,
                  sender=current_app.config['FLASKY_MAIL_SENDER'],
                  recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    mail.send(msg)