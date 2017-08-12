from flask_wtf import Form
from wtforms import StringField, SelectField, IntegerField, TextAreaField, FormField, SubmitField, FieldList, RadioField, SelectMultipleField, widgets, BooleanField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField

class RunConditionSubmitForm(Form):
    name  = StringField('Title of run condition',
                        validators=[DataRequired(message="Name required")])
    description = TextAreaField('Description')

class AnalysisSubmitForm(Form):
    title = StringField('Title',
                        validators=[DataRequired(message="Analysis title required")])
    collaboration = SelectField('Collaboration',
                                validators=[DataRequired(message="Collaboration required")])
    description = TextAreaField('Description',
                                validators=[DataRequired(message="Description required")])
    arxiv_id = StringField('ArXiv Id')
    doi = StringField('DOI')
    inspire_id = StringField('INSPIRE ID')
    cds_id = StringField('CDS ID')

class UserSubmitForm(Form):
    name = StringField('user name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

class RequestSubmitForm(Form):
    analysis_id = IntegerField('Analysis')
    title = StringField('Request title', validators=[DataRequired(message="Title required")])
    model_name = StringField('Model name', validators=[DataRequired(message="Model required")])
    reason_for_request = TextAreaField('Reason for request')
    additional_information = TextAreaField('Additional information')
    zenodo_deposition_id = StringField('Zenodo id')
    uuid = StringField('UUUID')

class MultipleCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

class SubscribeSubmitForm(Form):
    subscription_type= RadioField('Subscription type',
                                  choices=[('Provider', 'Provider'),
                                           ('Provider', 'Observer')],
                                  validators=[DataRequired(message="Subscription type required")])
    description = TextAreaField('Description')
    requirements = TextAreaField('Requirements')
    notifications = MultipleCheckboxField('Notifications',
                                          choices=[('Recast Requests', 'Recast Requests'),
                                                   ('Recast Responses', 'Recast Responses'),
                                                   ('New Subscribers to Analysis',
                                                    'New Subscribers to Analysis')]
                                          )
    authoritative = BooleanField('Authoritative')
    analysis_id = IntegerField('Analysis')

class ContactSubmitForm(Form):
    name = StringField('Your name',
                       validators=[DataRequired(message="Name required")])
    email = StringField('Your e-mail address',
                        validators=[DataRequired(message="Email required")])
    responder = StringField('To')
    responder_email = StringField('To (email)')
    subject = StringField('Subject')
    message = TextAreaField('Message',
                            validators=[DataRequired(message="Message required")])

class SignupSubmitForm(Form):
    email = StringField('Email address',
                        validators=[DataRequired(message="Email required")])
