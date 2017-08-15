from flask import render_template, flash
from flask_login import current_user

from pyedu.main import main
from pyedu.models import Lecture, User
from pyedu.util import sysinfo
from pyedu.forms import ChangePasswordForm


@main.route('/')
def index():
    lectures = Lecture.query.all()
    continue_task = current_user.get_next_task()
    return render_template('index.html', sysinfo=sysinfo(), lectures=lectures, continue_task=continue_task)


@main.route('/settings', defaults={'user_id':None}, methods=['GET', 'POST'])
@main.route('/settings/<int:user_id>', methods=['GET', 'POST'])
def settings(user_id):
    if user_id is None:
        user_id = current_user.id
    user = User.query.get_or_404(user_id)

    # check if password was changed
    pwform = ChangePasswordForm()
    if pwform.validate_on_submit():
        if user.verify_password(pwform.old_password.data):
            user.password = pwform.password.data
            flash('Password changed.', category='success')
        else:
            flash('The current password was not correct', category='danger')

    else:
        pwform.user_id.data = user_id

    # return the settings page
    return render_template('settings.html', pwform=pwform)