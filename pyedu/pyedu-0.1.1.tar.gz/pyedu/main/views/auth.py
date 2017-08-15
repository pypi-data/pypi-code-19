from datetime import datetime

from flask import render_template, flash, redirect, url_for, session
from flask_login import login_user, logout_user

from pyedu.app import login_manager
from pyedu.forms import LoginForm

from pyedu.main import main
from pyedu.models import User
from pyedu.util import  has_role


@main.route('/supersecret')
@has_role(role='teacher')
def supersecret():
    return '<h1>SUPER SECRET PAGE CONTENT</h1>'


@login_manager.user_loader
def load_user(username):
    return User.query.filter_by(username=username).first()


@main.route('/login/', methods=['GET', 'POST'])
@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # check if user has submitted the form
    if form.validate_on_submit():
        # get the user from db
        user = User.query.filter_by(username=form.username.data).first()

        if user is None:
            flash('The user %s does not exist.' % form.username.data, category='danger')
            return redirect(url_for('.login'))

        elif user.verify_password(form.password.data):
            login_user(user)
            session['login_at'] = datetime.utcnow()
            flash('Login successful. Welcome back %s' % user.username, category='success')

            return redirect(url_for('.index'))

        else:
            flash('The password is incorrect.', category='danger')
            form.password.data = ''
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@main.route('/logout/')
@main.route('/logout')
def logout():
    del session['login_at']
    logout_user()
    flash('You have been logged out.', category='info')
    return redirect(url_for('main.index'))