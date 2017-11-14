#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from threading import Thread

from flask import Flask
from flask import flash
from flask import redirect, render_template, url_for, session
from flask_bootstrap import Bootstrap
from flask_mail import Mail, Message
from flask_migrate import Migrate, MigrateCommand
from flask_moment import Moment
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import Required

from app import keys

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'

#数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] =\
        'sqlite:///' + os.path.join(basedir,'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

#email配置
app.config['MAIL_SERVER'] = keys.MAIL_SERVER
app.config['MAIL_PORT'] = keys.MAIL_PORT
app.config['MAIL_USE_TLS'] = keys.MAIL_USE_TLS
app.config['MAIL_USERNAME'] = keys.MAIL_USERNAME
app.config['MAIL_PASSWORD'] = keys.MAIL_PASSWORD
app.config['MAIL_SENDER'] = keys.MAIL_USERNAME
app.config['MAIL_SUBJECT_PREFIX'] = '[Flask Send]'
app.config['ADMIN'] = keys.ADMIN

db = SQLAlchemy(app)            #配置数据库
bootstrap = Bootstrap(app)      #配置模板
moment = Moment(app)            #配置时间
manager = Manager(app)
migrate = Migrate(app,db)       #数据库迁移
mail = Mail(app)                #配置邮件

manager.add_command('db',MigrateCommand)

@app.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        old_name = session.get('name',None)
        new_name = form.name.data
        user = User.query.filter_by(username=new_name).first()
        #检查数据库中的记录
        if user is None:
            user = User(username=new_name)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if app.config['ADMIN']:
                send_mail(app.config['ADMIN'],'New user register',
                          'mail/new_user',user=user)
        else:
            session['known'] = True
        #检查name是否改变
        if old_name is not None and old_name != new_name:
            flash("You have changed your name")
            session['name'] = new_name
        return redirect(url_for('index'))
    return render_template('index.html',form=form,
                           name=session.get('name',None),
                           known = session.get('known',False))

@app.route('/user/<name>')
def user(name):
    return render_template('user.html',name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404

@app.errorhandler(500)
def internal_sercer_error(e):
    return render_template('500.html'),500

#web表单
class NameForm(FlaskForm):
    name = StringField("What's your name?",validators=[Required()])
    submit = SubmitField('Submit')

#ORM数据表
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return '<User %r>' % self.username

#导入数据库实例及模型
def make_shell_context():
    return dict(app=app,db=db,Role=Role,User=User)

#电子邮件支持
def async_send_mail(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(to,subject,template,**kwargs):
    msg = Message(app.config['MAIL_SUBJECT_PREFIX'] + subject,
                  sender=app.config['MAIL_SENDER'],recipients=[to])

    msg.body = render_template(template+'.txt',**kwargs)
    msg.html = render_template(template+'.html',**kwargs)
    th = Thread(target=async_send_mail,args=(app,msg))
    th.start()
    return th

manager.add_command("shell",Shell(make_context=make_shell_context))     #导入数据库
manager.add_command("db",MigrateCommand)

if __name__ == '__main__':
    # manager.run()
    app.run(debug=True)
