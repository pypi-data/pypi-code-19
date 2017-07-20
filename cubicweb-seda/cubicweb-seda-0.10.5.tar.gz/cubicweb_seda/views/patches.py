# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""Dynamic patches to avoid hard dependancies on cubicweb releases"""

from logilab.common.decorators import monkeypatch

from cubicweb.web.views import autoform  # noqa


# monkey patch autoform to add an hidden field container the parent container eid that may be used
# in parent_and_container (see entities/__init__.py)

orig_autoform_init = autoform.AutomaticEntityForm.__init__


@monkeypatch(autoform.AutomaticEntityForm)
def __init__(self, *args, **kwargs):
    orig_autoform_init(self, *args, **kwargs)
    if 'peid' not in kwargs and self.edited_entity.cw_etype.startswith('SEDA'):  # main form
        parent = None
        if self.edited_entity.has_eid():
            parent = self.edited_entity
        elif '__linkto' in self._cw.form:
            parent = self._cw.entity_from_eid(int(self._cw.form['__linkto'].split(':')[1]))
        if parent is not None:
            if parent.cw_adapt_to('IContainer') is not None:
                container = parent
            else:
                container = parent.cw_adapt_to('IContained').container
            self.add_hidden(name='sedaContainerEID', value=container.eid, id='sedaContainerEID')


# this js file contains a custom implementation of addInlineCreationForm that propage
# sedaContainerEID
autoform.AutomaticEntityForm.needs_js += ('cubes.seda.form.js',)


# fix unexpected redirect after clicking on cancel in reledit ######################################
# (https://www.cubicweb.org/ticket/13120795)

from cubicweb.web.views import reledit  # noqa

orig_build_form = reledit.AutoClickAndEditFormView._build_form


@monkeypatch(reledit.AutoClickAndEditFormView)
def _build_form(*args, **kwargs):
    form, renderer = orig_build_form(*args, **kwargs)
    for button in getattr(form, 'form_buttons', ()):
        if button.label.endswith('cancel') and 'class' in button.attrs:
            button.attrs['class'] = button.attrs['class'].replace('cwjs-edition-cancel', '')
    return form, renderer


# auto-configuration of custom fields ##############################################################
# (https://www.cubicweb.org/ticket/14474840)
# other part in site_cubicweb

from cubicweb.web import formfields  # noqa
from cubicweb.web.views import forms  # noqa


@monkeypatch(forms.EntityFieldsForm, methodname='field_by_name')
@forms.iclassmethod
def field_by_name(cls_or_self, name, role=None, eschema=None):
    """return field with the given name and role. If field is not explicitly
    defined for the form but `eclass` is specified, guess_field will be
    called.
    """
    try:
        return super(forms.EntityFieldsForm, cls_or_self).field_by_name(name, role)
    except forms.form.FieldNotFound:
        if eschema is None or role is None or name not in eschema.schema:
            raise
        rschema = eschema.schema.rschema(name)
        # XXX use a sample target type. Document this.
        tschemas = rschema.targets(eschema, role)
        fieldclass = cls_or_self.uicfg_aff.etype_get(
            eschema, rschema, role, tschemas[0])
        kwargs = cls_or_self.uicfg_affk.etype_get(
            eschema, rschema, role, tschemas[0])
        if kwargs is None:
            kwargs = {}
        if fieldclass:
            if not isinstance(fieldclass, type):
                return fieldclass  # already an instance
            kwargs['fieldclass'] = fieldclass
        if isinstance(cls_or_self, type):
            req = None
        else:
            req = cls_or_self._cw
        field = formfields.guess_field(eschema, rschema, role, req=req, eidparam=True, **kwargs)
        if field is None:
            raise
        return field


# allow configuration of inlined form renderer using a class attribute #############################
# (https://www.cubicweb.org/ticket/15755515)

from logilab.common.decorators import cached  # noqa

autoform.InlineEntityEditionFormView.form_renderer_id = 'inline'


@monkeypatch(autoform.InlineEntityEditionFormView, methodname='form')
@property
@cached
def form(self):
    entity = self._entity()
    form = self._cw.vreg['forms'].select('edition', self._cw,
                                         entity=entity,
                                         formtype='inlined',
                                         form_renderer_id=self.form_renderer_id,
                                         copy_nav_params=False,
                                         mainform=False,
                                         parent_form=self.pform,
                                         **self.cw_extra_kwargs)
    if self.pform is None:
        form.restore_previous_post(form.session_key())
    self.add_hiddens(form, entity)
    return form
