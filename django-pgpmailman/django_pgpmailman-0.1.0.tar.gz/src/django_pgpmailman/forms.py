# -*- coding: utf-8 -*-
# Copyright (C) 2017 Jan Jancar
#
# This file is a part of the Django Mailman PGP plugin.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from django.utils.translation import ugettext_lazy as _
from pgpy import PGPKey
from pgpy.errors import PGPError


class NullBooleanRadioSelect(forms.RadioSelect):
    def value_from_datadict(self, data, files, name):
        value = data.get(name, None)
        return {'2': True,
                True: True,
                'True': True,
                '3': False,
                'False': False,
                False: False}.get(value, None)


boolean_choices = ((True, _('Yes')), (False, _('No')))
action_choices = (
    ('hold', _('Hold')),
    ('reject', _('Reject')),
    ('discard', _('Discard')),
    ('accept', _('Accept')),
    ('defer', _('Defer'))
)


class ListSignatureSettingsForm(forms.Form):
    sign_outgoing = forms.NullBooleanField(
            widget=NullBooleanRadioSelect(choices=boolean_choices),
            required=False,
            label=_('Sign outgoing messages'),
            help_text=_(
                    'Whether to sign the outgoing postings of a mailing list '
                    'by the list key.')
    )
    strip_original_sig = forms.NullBooleanField(
            widget=NullBooleanRadioSelect(choices=boolean_choices),
            required=False,
            label=_('Strip sender signature'),
            help_text=_('Whether to strip the original signature of a message'
                        '(if any).')
    )
    unsigned_msg_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Unsigned message action'),
            help_text=_(
                    'An action to take on an unsigned message. `Defer` lets '
                    'the message pass through to the next check.')
    )
    inline_pgp_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Inline PGP action'),
            help_text=_(
                    'An action to take on a message that is signed using '
                    'inline PGP. `Defer` lets the message pass through to the '
                    'next check.')
    )
    expired_sig_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Expired signature action'),
            help_text=_('An action to take on a message that has an expired '
                        'signature. `Defer` lets the message pass through to '
                        'the next check.')
    )
    revoked_sig_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Revoked signature action'),
            help_text=_('An action to take on a message that has a revoked '
                        'signature. `Defer` lets the message pass through to '
                        'the next check.')
    )
    invalid_sig_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Invalid signature action'),
            help_text=_('An action to take on a message with an invalid '
                        'signature. `Defer` lets the message pass through to '
                        'the next check.')
    )
    duplicate_sig_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Duplicate signature action'),
            help_text=_('An action to take on a message which contains a '
                        'signature that was already posted to a PGP enabled '
                        'mailing list before. `Defer` lets the message '
                        'pass through to the rest of the chain.')
    )


class ListEncryptionSettingsForm(forms.Form):
    encrypt_outgoing = forms.NullBooleanField(
            widget=NullBooleanRadioSelect(choices=boolean_choices),
            required=False,
            label=_('Encrypt outgoing messages'),
            help_text=_(
                    'Whether to encrypt the outgoing postings of a mailing '
                    'list to the subscribers keys.')
    )
    nonencrypted_msg_action = forms.ChoiceField(
            widget=forms.Select(),
            choices=action_choices,
            required=False,
            label=_('Nonencrypted message action'),
            help_text=_('An action to take on a nonencrypted message, is '
                        'done before executing the signature checks. `Defer` '
                        'lets the message pass through to signature checks.')
    )


key_change_choices = (('pgp-key-change-workflow', _('Default')),
                      ('pgp-key-change-mod-workflow',
                       _('Default, then moderate')))
member_role_choices = (('member', _('Member')),
                       ('owner', _('Owner')),
                       ('moderator', _('Moderator')),
                       ('nonmember', _('Nonmember')))


class ListMiscSettingsForm(forms.Form):
    key_change_workflow = forms.ChoiceField(
            widget=forms.Select(),
            choices=key_change_choices,
            required=False,
            label=_('Key change workflow'),
            help_text=_('A workflow to use for the key change operation. The '
                        'default workflow does the key confirmation the same '
                        'way the subscription process does. With possible '
                        'additional moderation.')
    )
    key_signing_allowed = forms.MultipleChoiceField(
            widget=forms.SelectMultiple(),
            choices=member_role_choices,
            required=False,
            label=_('Key signing allowed'),
            help_text=_('A set of member roles that are allowed to sign the '
                        'lists public key via the `key sign` command.')
    )


class KeyFileField(forms.FileField):
    def to_python(self, data):
        try:
            return PGPKey.from_blob(data.read())[0]
        except PGPError as e:
            raise ValidationError(str(e), code='invalid')


class ListKeyManagementForm(forms.Form):
    key = KeyFileField(
            widget=forms.ClearableFileInput(),
            required=False,
            label=_('Upload a new private key'),
            help_text=_('Useful for uploading a complately different list key '
                        'than the one generated by mailman-pgp, when setting '
                        'up a new mailing list. The uploaded key must be a '
                        'private PGP key, not expired and must be usable for '
                        'encryption and signatures.')
    )
    pubkey = KeyFileField(
            widget=forms.ClearableFileInput(),
            required=False,
            label=_('Upload a public key'),
            help_text=_('New signatures from the uploaded key are merged with '
                        'the current list key, provided the uploaded key '
                        'has the same key material and contains the UID that '
                        'was signed.')
    )


class ListCreateForm(forms.Form):
    listname = forms.CharField(
            label=_('List Name'),
            required=True,
            error_messages={
                'required': _('Please enter a name for your list.'),
                'invalid': _('Please enter a valid list name.')})
    mail_host = forms.ChoiceField()
    list_owner = forms.EmailField(
            label=_('Inital list owner address'),
            error_messages={
                'required': _(
                    'Please enter the list owner\'s email address.')},
            required=True)
    advertised = forms.ChoiceField(
            widget=forms.RadioSelect(),
            label=_('Advertise this list?'),
            error_messages={
                'required': _('Please choose a list type.')},
            required=True,
            choices=(
                (True, _('Advertise this list in list index')),
                (False, _('Hide this list in list index'))))
    description = forms.CharField(
            label=_('Description'),
            required=False)
    list_style = forms.ChoiceField()

    def __init__(self, domain_choices=None, style_choices=None,
                 *args, **kwargs):
        super(ListCreateForm, self).__init__(*args, **kwargs)
        self.fields['mail_host'] = forms.ChoiceField(
                widget=forms.Select(),
                label=_('Mail Host'),
                required=True,
                choices=domain_choices,
                error_messages={'required': _('Choose an existing Domain.'),
                                'invalid': _('Invalid mail host')})
        self.fields['list_style'] = forms.ChoiceField(
                widget=forms.Select(),
                label=_('List style'),
                required=True,
                choices=style_choices
        )
        if len(domain_choices) < 2:
            self.fields['mail_host'].help_text = _(
                    'Site admin has not created any domains')

    def clean_listname(self):
        try:
            validate_email(self.cleaned_data['listname'] + '@example.net')
        except:
            raise forms.ValidationError(_('Please enter a valid listname'))
        return self.cleaned_data['listname']
