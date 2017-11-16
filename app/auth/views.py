#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask import render_template,redirect,request,url_for,flash
from flask_login import login_user,logout_user,login_required,current_user

from .. import db
from . import auth
from ..models import User
from ..email import send_mail
from .forms import loginForm,RegistrationForm,ChangePasswordForm

@auth.route('/login',methods=['GET','POST'])
def login():
    form = loginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password')
    return render_template('auth/login.html',form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))

@auth.route('/register',methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        u = User(email = form.email.data,
                 password = form.password.data,
                 username = form.username.data)
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmed_token()
        send_mail(u.email,'Confirm Your Register','auth/email/confirm',user=u,token=token)
        flash('We have sent you a email to confirm your register,Please confirm and log in')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html',form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account.Thanks!')
    else:
        flash('The confirmation link is invalid or has expired')
    return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.endpoint[:5] != 'auth.' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/email/unconfirmed.html')

@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email,'Confirm Your Account',
              'auth/email/confirm',user=current_user,token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))

@auth.route('/change-password',methods=['GET','POST'])
@login_required
def change_password():
    change_form = ChangePasswordForm()
    if change_form.validate_on_submit():
        if current_user.verify_password(change_form.old_password.data):
            new_password = change_form.new_password.data
            current_user.password = new_password
            db.session.add(current_user)
            db.session.commit()
            flash('You have updated your password')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid password')
    return render_template('auth/change-password.html',form=change_form)

@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
