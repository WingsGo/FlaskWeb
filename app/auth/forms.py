#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField
from wtforms.validators import Required,Length,Email,Regexp,EqualTo
from wtforms import ValidationError

from ..models import User

class loginForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),
                                            Email()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me login in')
    submit = SubmitField('login in')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[Required(),Length(1,64),
                                            Email()])
    username = StringField('username',validators=[
        Required(),Length(1,64),Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                        'Usernames must have only letters, '
                                        'numbers, dots or underscores')])
    password = PasswordField('Password',validators=[
        Required(),EqualTo('password2',message='Password must match.')])
    password2 = PasswordField('Confirm password',validators=[Required()])
    submit = SubmitField('Register')

    def validate_email(self,field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')

    def validate_username(self,field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("old password",validators=[Required()])
    new_password = PasswordField('New password',validators=[Required()])
    conf_password = PasswordField('Confirm password',validators=[Required(),
                                                                 EqualTo('new_password',message='Password must match')])
    submit = SubmitField('Update password')