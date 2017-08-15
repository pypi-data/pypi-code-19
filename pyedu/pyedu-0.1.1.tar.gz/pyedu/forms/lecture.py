from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, HiddenField, SelectField
from wtforms.validators import DataRequired


class EditLectureForm(FlaskForm):
    id = HiddenField('id', default=None)
    name = StringField('Lecture Name', validators=[DataRequired()])
    description = TextAreaField('Lecture Description', default='No description found')
    save = SubmitField('Save')