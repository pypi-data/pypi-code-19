# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for app upgrades
"""

from __future__ import unicode_literals, absolute_import

import os

from sqlalchemy import orm

from rattail.db import model, Session as RattailSession
from rattail.time import make_utc
from rattail.threads import Thread
from rattail.upgrades import get_upgrade_handler

from deform import widget as dfwidget
from webhelpers2.html import tags

from tailbone.views import MasterView3 as MasterView
from tailbone.progress import SessionProgress


class UpgradeView(MasterView):
    """
    Master view for all user events
    """
    model_class = model.Upgrade
    executable = True
    downloadable = True

    grid_columns = [
        'created',
        'description',
        # 'not_until',
        'enabled',
        'executing',
        'executed',
        'executed_by',
    ]

    form_fields = [
        'description',
        # 'not_until',
        # 'requirements',
        'notes',
        'created',
        'created_by',
        'enabled',
        'executing',
        'executed',
        'executed_by',
        'stdout_file',
        'stderr_file',
    ]

    def __init__(self, request):
        super(UpgradeView, self).__init__(request)
        self.handler = self.get_handler()

    def get_handler(self):
        """
        Returns the ``UpgradeHandler`` instance for the view.  The handler
        factory for this may be defined by config, e.g.:

        .. code-block:: ini

           [rattail.upgrades]
           handler = myapp.upgrades:CustomUpgradeHandler
        """
        return get_upgrade_handler(self.rattail_config)

    def configure_grid(self, g):
        super(UpgradeView, self).configure_grid(g)
        g.set_joiner('executed_by', lambda q: q.join(model.User).outerjoin(model.Person))
        g.set_sorter('executed_by', model.Person.display_name)
        g.set_type('created', 'datetime')
        g.set_type('executed', 'datetime')
        g.default_sortkey = 'created'
        g.default_sortdir = 'desc'
        g.set_label('executed_by', "Executed by")
        g.set_link('created')
        g.set_link('description')
        # g.set_link('not_until')
        g.set_link('executed')

    def configure_form(self, f):
        super(UpgradeView, self).configure_form(f)
        f.set_type('created', 'datetime')
        f.set_type('enabled', 'boolean')
        f.set_type('executing', 'boolean')
        f.set_type('executed', 'datetime')
        # f.set_widget('not_until', dfwidget.DateInputWidget())
        f.set_widget('notes', dfwidget.TextAreaWidget(cols=80, rows=8))
        f.set_renderer('stdout_file', self.render_stdout_file)
        f.set_renderer('stderr_file', self.render_stdout_file)
        # f.set_readonly('created')
        # f.set_readonly('created_by')
        f.set_readonly('executing')
        f.set_readonly('executed')
        f.set_readonly('executed_by')
        f.set_label('stdout_file', "STDOUT")
        f.set_label('stderr_file', "STDERR")
        upgrade = f.model_instance
        if self.creating or self.editing:
            f.remove_field('created')
            f.remove_field('created_by')
            f.remove_field('stdout_file')
            f.remove_field('stderr_file')
            if self.creating or not upgrade.executed:
                f.remove_field('executing')
                f.remove_field('executed')
                f.remove_field('executed_by')
            if self.editing and upgrade.executed:
                f.remove_field('enabled')

        elif f.model_instance.executed:
            f.remove_field('enabled')
            f.remove_field('executing')

        else:
            f.remove_field('executed')
            f.remove_field('executed_by')
            f.remove_field('stdout_file')
            f.remove_field('stderr_file')

    def render_stdout_file(self, upgrade, fieldname):
        if fieldname.startswith('stderr'):
            filename = 'stderr.log'
        else:
            filename = 'stdout.log'
        path = self.rattail_config.upgrade_filepath(upgrade.uuid, filename=filename)
        if path:
            content = "{} ({})".format(filename, self.readable_size(path))
            url = '{}?filename={}'.format(self.get_action_url('download', upgrade), filename)
            return tags.link_to(content, url)
        return filename

    def get_size(self, path):
        try:
            return os.path.getsize(path)
        except os.error:
            return 0

    def readable_size(self, path):
        # TODO: this was shamelessly copied from FormAlchemy ...
        length = self.get_size(path)
        if length == 0:
            return '0 KB'
        if length <= 1024:
            return '1 KB'
        if length > 1048576:
            return '%0.02f MB' % (length / 1048576.0)
        return '%0.02f KB' % (length / 1024.0)

    def download_path(self, upgrade, filename):
        return self.rattail_config.upgrade_filepath(upgrade.uuid, filename=filename)

    def download_content_type(self, path, filename):
        return 'text/plain'

    def before_create_flush(self, upgrade):
        upgrade.created_by = self.request.user

    def execute_instance(self, upgrade, user, **kwargs):
        session = orm.object_session(upgrade)
        upgrade.executing = True
        session.commit()
        self.handler.execute(upgrade, user, **kwargs)
        upgrade.executing = False
        upgrade.executed = make_utc()
        upgrade.executed_by = user


def includeme(config):
    UpgradeView.defaults(config)
