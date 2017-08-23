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
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from six.moves.urllib_error import HTTPError

from django_pgpmailman.decorators import user_class_view
from django_pgpmailman.plugin import get_plugin


class UserSummaryView(TemplateView):
    template_name = 'django_pgpmailman/user/summary.html'

    @method_decorator(login_required)
    @user_class_view
    def dispatch(self, request, *args, **kwargs):
        return super(UserSummaryView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super(UserSummaryView, self).get_context_data(**kwargs)
        addresses = []
        for address in self.mm_user.addresses:
            try:
                addresses.append(get_plugin().get_address(address.email))
            except HTTPError:
                pass
        data['addresses'] = addresses
        return data
