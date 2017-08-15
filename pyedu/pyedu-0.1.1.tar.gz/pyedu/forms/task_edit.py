from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired

_default_solution = """# verify kwargs will be body content
def verify(**kwargs):
    pass
"""

_default_body = """# please fill all blank spaces
a = 
"""

class EditTaskForm(FlaskForm):
    id = HiddenField('id', default=None)
    lesson_id = HiddenField('lesson_id', default=None)
    name = StringField('Task Name', validators=[DataRequired()])
    description = TextAreaField('Task Description', validators=[DataRequired()])
    seq = StringField('Sequence', validators=[DataRequired()])
    body = TextAreaField('Task Code', validators=[DataRequired()], default=_default_body)
    solution = TextAreaField('Solution Code', validators=[DataRequired()], default=_default_solution)
    required = BooleanField('Task Required', default=True)
    submit = SubmitField('Save')

