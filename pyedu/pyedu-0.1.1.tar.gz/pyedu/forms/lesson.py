from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SubmitField
from wtforms.validators import DataRequired


class EditLessonForm(FlaskForm):
    id = HiddenField('id', default=None)
    lecture_id = HiddenField('lecture_id', default=None)
    name = StringField('Lesson Name', validators=[DataRequired()])
    submit = SubmitField('Save')