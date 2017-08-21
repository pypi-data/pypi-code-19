# -*- coding: utf-8 -*-
"""Agent Contact Portlet."""

# python imports
from email import message_from_string
from email.utils import (
    formataddr,
    getaddresses,
)
import copy
import logging
import re

# zope imports
from Acquisition import aq_inner
from Products.CMFPlone import PloneMessageFactory as PMF
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api
from plone.app.portlets.portlets import base
from plone.directives import form
from plone.formwidget.captcha.widget import CaptchaFieldWidget
from plone.formwidget.captcha.validator import CaptchaValidator
from plone.portlets.interfaces import IPortletDataProvider
from plone.z3cform import z2
from z3c.form import (
    button,
    field,
    validator,
)
from z3c.form.interfaces import (
    HIDDEN_MODE,
    IFormLayer,
)
from zope import schema
from zope.i18n import translate
from zope.interface import (
    Interface,
    Invalid,
    alsoProvides,
    implementer,
)
from zope.schema.fieldproperty import FieldProperty

# local imports
from plone.mls.listing import (
    PLONE_4,
    PLONE_5,
    PRODUCT_NAME,
)
from plone.mls.listing.browser.interfaces import IListingDetails
from plone.mls.listing.browser.tcwidget.widget import TCFieldWidget
from plone.mls.listing.i18n import _

# starting from 0.6.0 version plone.z3cform has IWrappedForm interface
try:
    from plone.z3cform.interfaces import IWrappedForm
    HAS_WRAPPED_FORM = True
except ImportError:
    HAS_WRAPPED_FORM = False

if PLONE_5:
    from plone.app.vocabularies.catalog import CatalogSource
elif PLONE_4:
    from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
    from plone.app.vocabularies.catalog import SearchableTextSourceBinder
    from zope import formlib


MSG_PORTLET_DESCRIPTION = _(
    u'This portlet shows a form to contact the corresponding agent for a '
    u'given listing via email.'
)

EMAIL_TEMPLATE = _(
    u'agent_contact_email',
    default=u'Enquiry from: {name} <{sender_from_address}>\n'
    u'Listing URL: {url}\n'
    u'\n'
    u'{form_data}\n'
    u'\n'
    u'Message:\n'
    u'{message}'
)

EMAIL_TEMPLATE_AGENT = _(
    u'agent_contact_email_agent',
    default=u'The responsible agent for this listing is '
    u'{agent} ({profile}).\n'
    u'\n'
    u'Please contact {agent} at {agent_email}.'
)


check_email = re.compile(
    r'[a-zA-Z0-9._%-]+@([a-zA-Z0-9-]+\.)*[a-zA-Z]{2,4}').match

check_for_url = re.compile(
    r'http[s]?://').search

logger = logging.getLogger(PRODUCT_NAME)


def validate_accept(value):
    if value is not True:
        return False
    return True


def validate_email(value):
    if value:
        if not check_email(value):
            raise Invalid(_(u'Invalid email address'))
    return True


def contains_nuts(value):
    """Check for traces of nuts, like urls or other spammer fun things"""
    if value:
        if check_for_url(value):
            raise Invalid(_(u'No Urls allowed'))
    return True


class IEmailForm(Interface):
    """Email Form schema."""

    subject = schema.TextLine(
        required=False,
        title=PMF(u'label_subject', default=u'Subject')
    )

    name = schema.TextLine(
        description=PMF(
            u'help_sender_fullname',
            default=u'Please enter your full name',
        ),
        required=True,
        title=PMF(u'label_name', default=u"Name"),
    )

    sender_from_address = schema.TextLine(
        constraint=validate_email,
        description=PMF(
            u'help_sender_from_address',
            default=u'Please enter your e-mail address',
        ),
        required=True,
        title=PMF(u'label_sender_from_address', default=u'E-Mail'),
    )

    country = schema.TextLine(
        description=_(u'Please enter your country of residence.'),
        required=True,
        title=_(u'Country'),
    )

    zipcode = schema.TextLine(
        description=_(u'Please enter your ZIP code.'),
        required=False,
        title=_(u'ZIP'),
    )

    phone = schema.TextLine(
        description=_(
            u'Please enter a phone number. Some agents will not respond '
            u'without one.'
        ),
        missing_value=u'-',
        required=False,
        title=_(u'Phone Number'),
    )

    arrival_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Arrival Date'),
    )

    departure_date = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Departure Date'),
    )

    adults = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Adults'),
    )

    children = schema.TextLine(
        missing_value=u'-',
        required=False,
        title=_(u'Children'),
    )

    message = schema.Text(
        constraint=contains_nuts,
        description=PMF(
            u'help_message',
            default=u'Please enter the message you want to send.',
        ),
        max_length=1000,
        required=True,
        title=PMF(u'label_message', default=u'Message'),
    )

    captcha = schema.TextLine(
        required=True,
        title=_(u'Captcha'),
    )

    accept_tcs = schema.Bool(
        constraint=validate_accept,
        required=True,
        title=_(u'I accept the Terms & Conditions'),
    )


class EmailForm(form.Form):
    """Email Form."""
    fields = field.Fields(IEmailForm).omit(
        'country',
        'zipcode',
        'accept_tcs',
        'arrival_date',
        'departure_date',
        'adults',
        'children',
    )
    ignoreContext = True
    method = 'post'
    _email_sent = False

    def __init__(self, context, request, portlet_hash=None, info=None,
                 data=None):
        super(EmailForm, self).__init__(context, request)
        self.listing_info = info
        self.data = data
        if portlet_hash:
            self.prefix = portlet_hash + '.' + self.prefix
        self.check_for_spam = data.reject_links

    @property
    def already_sent(self):
        return self._email_sent

    @property
    def is_residential_lease(self):
        return self.listing_info.get('listing_id', '').lower().startswith('rl')

    def update(self):
        omitted = []
        if not self.is_residential_lease:
            omitted = [
                'arrival_date',
                'departure_date',
                'adults',
                'children',
            ]
        if not self.data.country_visible:
            omitted.append('country')
        if not self.data.zipcode_visible:
            omitted.append('zipcode')
        if not self.data.accept_tcs_visible:
            omitted.append('accept_tcs')
        if not self.data.captcha_visible:
            omitted.append('captcha')

        self.fields = field.Fields(IEmailForm).omit(*omitted)

        if 'accept_tcs' in self.fields:
            self.fields['accept_tcs'].widgetFactory = TCFieldWidget

        if 'captcha' in self.fields:
            self.fields['captcha'].widgetFactory = CaptchaFieldWidget
        super(EmailForm, self).update()

    def updateWidgets(self):
        super(EmailForm, self).updateWidgets()
        portal = api.portal.get()
        subject = u'{portal_title}: {title} ({lid})'.format(
            lid=self.listing_info['listing_id'],
            portal_title=portal.getProperty('title').decode('utf-8'),
            title=self.listing_info['listing_title'],
        )
        self.widgets['subject'].mode = HIDDEN_MODE
        self.widgets['subject'].value = subject
        if 'accept_tcs' in self.widgets:
            self.widgets['accept_tcs'].target = self.data.accept_tcs_target

        if not self.check_for_spam:
            schema_field = copy.copy(self.widgets['message'].field)
            schema_field.constraint = lambda x: True
            self.widgets['message'].field = schema_field

        if self.data.phone_required:
            phone_field = copy.copy(self.widgets['phone'].field)
            phone_field.required = True
            self.widgets['phone'].field = phone_field
            self.widgets['phone'].required = True

    @button.buttonAndHandler(PMF(u'label_send', default='Send'), name='send')
    def handle_send(self, action):
        """Send button for sending the email."""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        if 'captcha' in data:
            # Verify the user input against the captcha
            captcha = CaptchaValidator(
                self.context, self.request, None, IEmailForm['captcha'], None,
            )
            if not self.already_sent and captcha.validate(data['captcha']):
                self.send_email(data)
                self._email_sent = True
        else:
            if not self.already_sent:
                self.send_email(data)
                self._email_sent = True
        return

    def format_data_for_email(self, data):
        """Add the submitted form data to the mail message."""
        items = []
        tpl = u'{0}: {1}\n'
        if 'country' in data:
            items.append(
                tpl.format(
                    translate(_(u'Country'), context=self.request),
                    data['country'],
                )
            )
        if 'zipcode' in data:
            items.append(
                tpl.format(
                    translate(_(u'ZIP'), context=self.request),
                    data['zipcode'],
                )
            )
        if 'phone' in data:
            items.append(
                tpl.format(
                    translate(_(u'Phone Number'), context=self.request),
                    data['phone'],
                )
            )

        if 'arrival_date' in data:
            items.append(
                tpl.format(
                    translate(_(u'Arrival Date'), context=self.request),
                    data['arrival_date'],
                )
            )
        if 'departure_date' in data:
            items.append(
                tpl.format(
                    translate(_(u'Departure Date'), context=self.request),
                    data['departure_date'],
                )
            )
        if 'adults' in data:
            items.append(
                tpl.format(
                    translate(_(u'Adults'), context=self.request),
                    data['adults'],
                )
            )
        if 'children' in data:
            items.append(
                tpl.format(
                    translate(_(u'Children'), context=self.request),
                    data['children'],
                )
            )
        if 'accept_tcs' in data:
            items.append(
                tpl.format(
                    translate(
                        _(u'Terms & Conditions accepted'),
                        context=self.request,
                    ),
                    data['accept_tcs']
                )
            )
        return u''.join(items)

    def send_email(self, data):
        """Construct and send an email message."""
        portal = api.portal.get()

        try:
            email_charset = api.portal.get_registry_record('plone.email_charset')
        except api.exc.InvalidParameterError:
            email_charset = portal.getProperty('email_charset', 'utf-8')

        recipient = None
        try:
            portal_address = api.portal.get_registry_record(
                'plone.email_from_address'
            )
        except api.exc.InvalidParameterError:
            # Before Plone 5.0b2 these were stored in portal_properties
            portal_address = portal.getProperty('email_from_address', '')
        custom_recipient = getattr(self.data, 'recipient', None)

        if custom_recipient is not None:
            recipient = custom_recipient
        else:
            agent = self.listing_info.get('agent')
            try:
                recipient = agent.get('agent_email').get('value')
            except AttributeError:
                recipient = None

        if recipient is None:
            recipient = portal_address

        recipients = [recipient]
        if getattr(self.data, 'bcc', None) is not None:
            bcc = self.data.bcc
            recipients += [formataddr(addr) for addr in getaddresses((bcc, ))]

        sender = formataddr((data['name'], data['sender_from_address']))

        overridden = self.listing_info.get('overridden', False)
        if overridden is True or custom_recipient is not None:
            orig_agent = self.listing_info.get('original_agent')
            agent = translate(
                EMAIL_TEMPLATE_AGENT,
                context=self.request,
            ).format(
                agent=orig_agent.get('name').get('value'),
                agent_email=orig_agent.get('agent_email').get('value'),
                profile=orig_agent.get('profile'),
            )
            data['message'] = '\n'.join([data['message'], agent])
        data['form_data'] = self.format_data_for_email(data)
        data['url'] = self.request.getURL()

        subject = data['subject']

        body = translate(
            EMAIL_TEMPLATE,
            context=self.request,
        ).format(**data)
        email_msg = message_from_string(body.encode(email_charset))
        email_msg['To'] = formataddr((recipient, recipient))

        api.portal.send_email(
            sender=sender,
            recipient=recipients,
            subject=subject,
            body=email_msg,
        )


# Register Captcha validator for the captcha field in the ICaptchaForm
validator.WidgetValidatorDiscriminators(
    CaptchaValidator, field=IEmailForm['captcha'])


class IAgentContactPortlet(IPortletDataProvider):
    """A portlet which sends an email to the agent."""

    heading = schema.TextLine(
        description=_(
            u'Custom title for the portlet. If no title is provided, the '
            u'default title is used.'
        ),
        required=False,
        title=_(u'Portlet Title'),
    )

    description = schema.Text(
        description=_(u'Additional description for the portlet.'),
        required=False,
        title=_('Description'),
    )

    country_visible = schema.Bool(
        required=False,
        title=_(u'Show Country field in email form?')
    )

    zipcode_visible = schema.Bool(
        required=False,
        title=_(u'Show ZIP field in email form?')
    )

    phone_required = schema.Bool(
        required=False,
        title=_(u'Make phone field in email form required?'),
    )

    accept_tcs_visible = schema.Bool(
        required=False,
        title=_(u'Show Accept Terms & Conditions field in email form?')
    )

    if PLONE_5:
        accept_tcs_target = schema.Choice(
            required=False,
            source=CatalogSource(),
            title=_(u'Terms & Conditions page'),
        )
    elif PLONE_4:
        accept_tcs_target = schema.Choice(
            required=False,
            source=SearchableTextSourceBinder({}, default_query='path:'),
            title=_(u'Terms & Conditions page'),
        )

    captcha_visible = schema.Bool(
        default=True,
        required=False,
        title=_(u'Show Captcha field in email form?'),
    )

    mail_sent_msg = schema.Text(
        description=_(
            u'Thank you message that is shown after the mail was sent.'
        ),
        required=False,
        title=_(u'Mail Sent Message'),
    )

    recipient = schema.TextLine(
        constraint=validate_email,
        description=_(
            u'Override the recipient e-mail address. Leave blank to use the '
            u'e-mail address from the agent information.'
        ),
        required=False,
        title=_(u'Override Recipient'),
    )

    bcc = schema.TextLine(
        description=_(
            u'E-mail addresses which receive a blind carbon copy (comma '
            u'separated).'
        ),
        required=False,
        title=_(u'BCC Recipients'),
    )

    reject_links = schema.Bool(
        default=True,
        description=_(
            u'Activate for Spam Protection. Any attempt to use a link inside '
            u'this form will raise a validation error.'
        ),
        required=False,
        title=_(u'Reject Text with Links?'),
    )


@implementer(IAgentContactPortlet)
class Assignment(base.Assignment):
    """Agent Contact Portlet Assignment."""

    heading = FieldProperty(IAgentContactPortlet['heading'])
    description = FieldProperty(IAgentContactPortlet['description'])
    country_visible = FieldProperty(IAgentContactPortlet['country_visible'])
    zipcode_visible = FieldProperty(IAgentContactPortlet['zipcode_visible'])
    phone_required = FieldProperty(IAgentContactPortlet['phone_required'])
    accept_tcs_visible = FieldProperty(
        IAgentContactPortlet['accept_tcs_visible']
    )
    accept_tcs_target = None
    captcha_visible = FieldProperty(IAgentContactPortlet['captcha_visible'])
    mail_sent_msg = FieldProperty(IAgentContactPortlet['mail_sent_msg'])
    recipient = FieldProperty(IAgentContactPortlet['recipient'])
    bcc = FieldProperty(IAgentContactPortlet['bcc'])
    reject_links = FieldProperty(IAgentContactPortlet['reject_links'])

    title = _(u'MLS: Agent Contact')

    def __init__(
        self,
        heading=None,
        description=None,
        country_visible=None,
        zipcode_visible=None,
        phone_required=None,
        accept_tcs_visible=None,
        accept_tcs_target=None,
        captcha_visible=None,
        mail_sent_msg=None,
        recipient=None,
        bcc=None,
        reject_links=None,
    ):
        self.heading = heading
        self.description = description
        self.country_visible = country_visible
        self.zipcode_visible = zipcode_visible
        self.phone_required = phone_required
        self.accept_tcs_visible = accept_tcs_visible
        self.accept_tcs_target = accept_tcs_target
        self.captcha_visible = captcha_visible
        self.mail_sent_msg = mail_sent_msg
        self.recipient = recipient
        self.bcc = bcc
        self.reject_links = reject_links


class Renderer(base.Renderer):
    """Agent Contact Portlet Renderer."""

    if PLONE_5:
        render = ViewPageTemplateFile('templates/p5_agent_contact.pt')
    elif PLONE_4:
        render = ViewPageTemplateFile('templates/agent_contact.pt')

    @property
    def already_sent(self):
        return self.form.already_sent

    @property
    def available(self):
        return IListingDetails.providedBy(self.view) and \
            getattr(self.view, 'listing_id', None) is not None

    @property
    def description(self):
        return self.data.description

    @property
    def mail_sent_msg(self):
        return self.data.mail_sent_msg or PMF(u'Mail sent.')

    @property
    def title(self):
        return self.data.heading or _(u'Agent Contact')

    @property
    def can_send_email(self):
        portal = api.portal.get()

        ctrlOverview = api.content.get_view(
            context=portal,
            request=portal.REQUEST,
            name='overview-controlpanel',
        )
        if ctrlOverview.mailhost_warning():
            return False
        return True

    def update(self):
        if self.view.info is None:
            return
        listing_info = {
            'listing_id': self.view.info.get('id').get('value'),
            'listing_title': self.view.info.get('title').get('value'),
            'agent': self.view.contact.get('agent'),
            'original_agent': self.view.contact.get('original_agent'),
            'overridden': self.view.contact.get('overridden', False),
        }

        z2.switch_on(self, request_layer=IFormLayer)
        portlet_hash = self.__portlet_metadata__.get('hash')
        self.form = EmailForm(aq_inner(self.context), self.request,
                              portlet_hash, listing_info, self.data)
        if HAS_WRAPPED_FORM:
            alsoProvides(self.form, IWrappedForm)
        self.form.update()


class AddForm(base.AddForm):
    """Add form for the Agent Contact portlet."""
    if PLONE_5:
        schema = IAgentContactPortlet
    elif PLONE_4:
        form_fields = formlib.form.Fields(IAgentContactPortlet)
        form_fields['accept_tcs_target'].custom_widget = UberSelectionWidget
    label = _(u'Add Agent Contact portlet')
    description = MSG_PORTLET_DESCRIPTION

    def create(self, data):
        assignment = Assignment()
        if PLONE_4:
            formlib.form.applyChanges(assignment, self.form_fields, data)
        return assignment


class EditForm(base.EditForm):
    """Edit form for the Agent Contact portlet"""
    if PLONE_5:
        schema = IAgentContactPortlet
    elif PLONE_4:
        form_fields = formlib.form.Fields(IAgentContactPortlet)
        form_fields['accept_tcs_target'].custom_widget = UberSelectionWidget
    label = _(u'Edit Agent Contact portlet')
    description = MSG_PORTLET_DESCRIPTION
