#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .. import db
from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import Required


class NameForm(FlaskForm):
    name = StringField("What's your name?",validators=[Required()])
    submit = SubmitField("submit")
