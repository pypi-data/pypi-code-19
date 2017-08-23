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

from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.base import ContentFile
from django.http import HttpResponse, Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import FormView
from six.moves.urllib.error import HTTPError

from django_pgpmailman.decorators import (list_view, list_class_view,
                                          member_role_required)
from django_pgpmailman.forms import (ListSignatureSettingsForm,
                                     ListEncryptionSettingsForm,
                                     ListMiscSettingsForm,
                                     ListKeyManagementForm, ListCreateForm)
from django_pgpmailman.plugin import get_plugin, get_client


def pgp_list_index(request):
    return render(request, 'django_pgpmailman/index.html',
                  {'lists': get_plugin().lists})


@list_view
def pgp_list_summary(request, pgp_list):
    return render(request, 'django_pgpmailman/list/summary.html',
                  {'pgp_list': pgp_list})


class ListCreate(FormView):
    template_name = 'django_pgpmailman/list/create.html'
    form_class = ListCreateForm
    initial = {'advertised': True}

    def get_initial(self):
        self.initial.update({'list_owner': self.request.user.email})
        return super(ListCreate, self).get_initial()

    def get_form_kwargs(self):
        kwargs = super(ListCreate, self).get_form_kwargs()
        domains = []
        for domain in get_client().domains:
            domains.append((domain.mail_host, domain.mail_host))
        kwargs['domain_choices'] = domains
        styles = [('pgp-default', 'PGP discussion'),
                  ('pgp-announce', 'PGP announce')]
        kwargs['style_choices'] = styles
        return kwargs

    @user_passes_test(lambda u: u.is_superuser)
    def dispatch(self, request, *args, **kwargs):
        return super(ListCreate, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            client = get_client()
            domain = client.get_domain(
                    mail_host=form.cleaned_data['mail_host'])

            mlist = domain.create_list(form.cleaned_data['listname'],
                                       style_name=form.cleaned_data[
                                           'list_style'])
            mlist.add_owner(form.cleaned_data['list_owner'])
            list_settings = mlist.settings
            if form.cleaned_data['description']:
                list_settings['description'] = form.cleaned_data['description']
            list_settings['advertised'] = form.cleaned_data['advertised']
            list_settings.save()

            self.mlist = mlist
            messages.success(self.request, _('List created'))
        except HTTPError as e:
            messages.error(self.request, e.msg)

        return super(ListCreate, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url,
                       kwargs=dict(list_id=self.mlist.list_id))


class ListKey(View):
    which_key = None

    def get(self, request):
        key = getattr(self.pgp_list, self.which_key)
        if key is None:
            raise Http404
        key_file = ContentFile(str(key))
        response = HttpResponse(key_file, 'application/pgp-keys')
        length = key_file.size
        disposition = 'attachment; filename="%s.asc"' % self.pgp_list.list_id
        response['Content-Length'] = length
        response['Content-Disposition'] = disposition
        return response


class ListPubkey(ListKey):
    which_key = 'pubkey'

    @list_class_view
    def dispatch(self, request, *args, **kwargs):
        return super(ListKey, self).dispatch(request, *args, **kwargs)


class ListPrivkey(ListKey):
    which_key = 'key'

    @method_decorator(login_required)
    @list_class_view
    @member_role_required('owner')
    def dispatch(self, request, *args, **kwargs):
        return super(ListPrivkey, self).dispatch(request, *args, **kwargs)


class ListSettings(FormView):
    properties = None

    def get_initial(self):
        result = {}
        for key in self.properties:
            result[key] = getattr(self.pgp_list, key, None)
        return result

    def get_context_data(self, **kwargs):
        data = super(ListSettings, self).get_context_data(
                **kwargs)
        data['pgp_list'] = self.pgp_list
        data['mlist'] = self.pgp_list.mlist
        return data

    @method_decorator(login_required)
    @list_class_view
    @member_role_required('owner')
    def dispatch(self, request, *args, **kwargs):
        return super(ListSettings, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not form.changed_data:
            return

        for key in form.changed_data:
            if form.cleaned_data[key] is not None:
                setattr(self.pgp_list, key, form.cleaned_data[key])

        try:
            self.pgp_list.save()

            if form.has_changed():
                messages.success(
                        self.request, _('List settings have been updated.'))
            else:
                messages.info(self.request, _('List settings did not change.'))

        except HTTPError as e:
            messages.error(self.request, e.msg)

        return super(ListSettings, self).form_valid(form)

    def get_success_url(self):
        return reverse(self.success_url,
                       kwargs=dict(list_id=self.pgp_list.list_id))


class ListSignatureSettingsView(ListSettings):
    form_class = ListSignatureSettingsForm
    template_name = 'django_pgpmailman/list/signature_settings.html'
    properties = ('sign_outgoing', 'strip_original_sig', 'unsigned_msg_action',
                  'inline_pgp_action', 'expired_sig_action',
                  'revoked_sig_action', 'invalid_sig_action',
                  'duplicate_sig_action')


class ListEncryptionSettingsView(ListSettings):
    form_class = ListEncryptionSettingsForm
    template_name = 'django_pgpmailman/list/encryption_settings.html'
    properties = ('nonencrypted_msg_action', 'encrypt_outgoing')


class ListMiscSettingsView(ListSettings):
    form_class = ListMiscSettingsForm
    template_name = 'django_pgpmailman/list/misc_settings.html'
    properties = ('key_change_workflow', 'key_signing_allowed')


class ListKeyManagementView(ListSettings):
    form_class = ListKeyManagementForm
    template_name = 'django_pgpmailman/list/key_management.html'
    properties = ('key', 'pubkey')
