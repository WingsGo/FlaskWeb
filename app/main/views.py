#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from datetime import datetime
from flask import render_template,session,redirect,url_for

from . import main
from .forms import NameForm
from .. import db
from ..models import User

@main.route('/',methods=['GET','POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        return redirect(url_for('.index'))