from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, HiddenField
from wtforms.validators import DataRequired, EqualTo


class ChangePasswordForm(FlaskForm):
    user_id = HiddenField('user_id')
    old_password = PasswordField('Old password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired(),
                                                         EqualTo('password2', message='Passwords did not match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Change')