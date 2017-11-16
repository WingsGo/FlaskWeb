#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from . import mail
from threading import Thread
from flask import render_template,current_app
from flask_mail import Message

def async_send_mail(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kwargs):
    app = current_app._get_current_object()
    msg = Message(subject=subject,recipients=[to],sender=app.config['MAIL_SENDER'])
    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    th = Thread(target=async_send_mail,args=(app,msg))
    th.start()