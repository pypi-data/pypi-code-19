from flask_wtf import FlaskForm
from wtforms import HiddenField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class ViewTaskForm(FlaskForm):
    id = HiddenField('id', validators=[DataRequired()])
    body = TextAreaField('body', validators=[DataRequired()])
    submit = SubmitField('Execute')