"""This is an example Blueprint for a pretty standard user setup. """

from flask import (Blueprint, request, render_template, flash, url_for, send_from_directory, make_response,
                   redirect, current_app, abort)
from flaskapp.extensions import db

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField, SubmitField, validators
from datetime import datetime, timedelta

import os
from .user_mixin import authenticate
from .activator_token import ActivatorToken
import secrets
"""
Some things are safe to handle at the controller level: the auth is secure and extensible
For example: the login form can have a logo. The password reset boxes can have support
links, etc, but fundamentally auth is all handled through these methods.

Something like admin user invites needs to be handled in the application code.

"""

templates_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
blueprint = Blueprint('auth', __name__, template_folder=templates_folder)


class DefaultLoginForm(FlaskForm):
    email = StringField('Your e-mail address:', [validators.InputRequired(), validators.Email('Must be a valid email.')])
    password = PasswordField("Password", [validators.InputRequired()])


@blueprint.route('/login', methods=['GET', 'POST'])
@authenticate(mode='public')
def standard_login_required(user_obj=None):
    """
        Example login form that's used as the default:
    """
 
    # Automaically forward if the user is logged in accessing this page for some reason.
    if user_obj:
        return redirect(user_obj.after_login_redirect_desintation())

    form = DefaultLoginForm()

    if request.method == 'POST' and form.validate():
        client_key = request.cookies.get('client_key')

        from fuser.client import Client
        client = Client.create_with_credentials(email=form.email.data,
                                                password=form.password.data,
                                                client_key=client_key)
        db.session.add(client)
        db.session.commit()
        # Successful login:
        if client:
            return redirect(client.user.after_login_redirect_desintation())
        else:
            form.password.errors.append('Invalid credentials')

        return make_response(render_template('default_login.html', form=form))

    else:
        response = make_response(render_template('fuser_default_login.html', form=form))
        response.set_cookie('client_key',
                            value=secrets.token_urlsafe(20), 
                            expires=datetime.utcnow() + timedelta(days=180))
        return response




class DefaultAdminInviteForm(FlaskForm):
    email = StringField('New User\'s email address', 
                        [validators.InputRequired(), 
                        validators.Email('your@email.com')])
    is_admin = BooleanField('Is an Admin?', 
                        [validators.InputRequired()])



@blueprint.route('/auth/request_password_change', methods=['GET', 'POST'])
@authenticate(mode='valid')
def reset_password(token, user_obj=None):
    """From either setting up initially"""

    class ResetPasswordForm(FlaskForm):
        email = StringField('Your e-mail address:', [validators.InputRequired(), validators.Email('Must be a valid email.')])

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate():
        matching_user = User.query.filter_by(email=form.email).filter_by(is_active=True).first()

        matching_user.send_default_activator_email('reset')

    return make_response(render_template('fuser_request_password_change.html', form=form))



@blueprint.route('/auth/set_password/<string:token>', methods=['GET', 'POST'])
@authenticate(mode='public')
def set_password(token, user_obj=None):
    """From either setting up initially"""

    class SetPasswordForm(FlaskForm):
        password = PasswordField(
            'Password',
            [
                validators.Length(min=5),
                validators.InputRequired(),
                validators.EqualTo('confirm', message='Passwords must match')
            ])
        confirm = PasswordField('Repeat password')

    matching_activator = ActivatorToken.query.filter_by(activator_code=token).filter_by(is_active=True).first()
    if matching_activator:
        if not matching_activator.is_expired():
            form = SetPasswordForm()

            if request.method == 'POST' and form.validate():
                client_key = request.cookies.get('client_key')

                matching_activator.user.set_password(form.password.data)
                matching_activator.is_valid = False
                db.session.add(matching_activator)
                db.session.add(matching_activator.user)
                db.session.commit()

                from fuser.client import Client
                client = Client.create_with_credentials(email=matching_activator.user.email,
                                                        password=form.password.data,
                                                        client_key=client_key)
                db.session.add(client)
                db.session.commit()
                return redirect(client.user.after_login_redirect_desintation())

            else: # GET REQUEST
                response = make_response(render_template('fuser_set_password.html', form=form, token=token))
                if request.cookies.get('client_key') == "" or request.cookies.get('client_key') == None:
                    response.set_cookie('client_key',
                                        value=secrets.token_urlsafe(20), 
                                        expires=datetime.utcnow() + timedelta(days=180))
                return response

            return make_response(render_template('fuser_set_password.html', form=form, token=token))
    return make_response(render_template('fuser_set_password.html', invalid_token=True))


@blueprint.route('/logout', methods=['GET', 'POST'])
@authenticate(mode='valid')
def logout(user_obj):
    from fuser.client import Client

    client_key = request.cookies.get('client_key')
    matching_client = Client.query.filter_by(client_key=client_key).one()
    matching_client.is_active = False
    db.session.add(matching_client)
    db.session.commit()
    return redirect('/')





