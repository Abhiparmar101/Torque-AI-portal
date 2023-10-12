# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for,session
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass
import secrets
import jwt
@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication_blueprint.login'))


# Login & Registration

@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = Users.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):

            login_user(user)
            return redirect(url_for('authentication_blueprint.route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html',
                               msg='Wrong user or password',
                               form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('home_blueprint.index'))

def generate_new_session_id():
        return secrets.token_hex(16)
def generate_token(user_id):
    payload = {
        'user_id': user_id,
        #'exp': datetime.utcnow() + timedelta(days=1)  # Token expiration time
    }
    token = jwt.encode(payload, algorithm='HS256')
    return token
@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check usename exists
        user = Users.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = Users.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)
        session_id = generate_new_session_id()
        # else we can create the user
        user = Users(session_id=session_id,**request.form)
        db.session.add(user)
        db.session.commit()
        session['sid'] =user.session_id
        # Delete user from session
        logout_user()
        
        return render_template('accounts/register.html',
                               msg='User created successfully.',
                               success=True,
                               form=create_account_form,
                               session_id=session_id)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@blueprint.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('authentication_blueprint.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('pages/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('pages/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('pages/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('pages/page-500.html'), 500
