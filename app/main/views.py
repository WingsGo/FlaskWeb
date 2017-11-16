#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ..decorators import admin_required,permission_required
from ..models import Permission

from flask_login import login_required
from flask import render_template,session,redirect,url_for,abort

from . import main
from ..models import User

@main.route('/',methods=['GET','POST'])
def index():
    return render_template('index.html')

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template('user.html',user=user)

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "For administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"