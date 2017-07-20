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

from logilab.common.decorators import monkeypatch

# hack to avoid crash when cube is installed in a directory specified by CW_CUBES_PATH, because
# `RegistrableInstance` attempt to compute its __module__, but in that case the file isn't in the
# python path. This should go away once cubes become regular packages.

import traceback

from logilab.common import registry

from cubicweb import rtags
from cubicweb.entity import Entity


@monkeypatch(registry.RegistrableInstance, methodname='__new__')
@staticmethod
def __new__(cls, *args, **kwargs):
    """Add a __module__ attribute telling the module where the instance was
    created, for automatic registration.
    """
    module = kwargs.pop('__module__', None)
    self = super(registry.RegistrableInstance, cls).__new__(cls)
    if module is None:
        filepath = traceback.extract_stack(limit=2)[0][0]
        module = registry._modname_from_path(filepath)
    self.__module__ = module
    return self


@monkeypatch(rtags.RelationTags)
def __init__(self, __module__=None):
    super(rtags.RelationTags, self).__init__()
    self._tagdefs = {}


Entity.cw_skip_copy_for.append(('container', 'subject'))
Entity.cw_skip_copy_for.append(('container', 'object'))
Entity.cw_skip_copy_for.append(('clone_of', 'subject'))
Entity.cw_skip_copy_for.append(('clone_of', 'object'))


# auto-configuration of custom fields ##############################################################
# (https://www.cubicweb.org/ticket/14474840)
# other part in views/patches

from cubicweb.web import formfields  # noqa


@monkeypatch(formfields)  # noqa
def guess_field(eschema, rschema, role='subject', req=None, **kwargs):
    """This function return the most adapted field to edit the given relation
    (`rschema`) where the given entity type (`eschema`) is the subject or object
    (`role`).

    The field is initialized according to information found in the schema,
    though any value can be explicitly specified using `kwargs`.
    """
    fieldclass = None
    rdef = eschema.rdef(rschema, role)
    if role == 'subject':
        targetschema = rdef.object
        if rschema.final:
            if rdef.get('internationalizable'):
                kwargs.setdefault('internationalizable', True)
    else:
        targetschema = rdef.subject
    card = rdef.role_cardinality(role)
    composite = getattr(rdef, 'composite', None)
    kwargs['name'] = rschema.type
    kwargs['role'] = role
    kwargs['eidparam'] = True
    # don't mark composite relation as required, we want the composite element
    # to be removed when not linked to its parent
    kwargs.setdefault('required', card in '1+' and composite != formfields.neg_role(role))
    if role == 'object':
        kwargs.setdefault('label', (eschema.type, rschema.type + '_object'))
    else:
        kwargs.setdefault('label', (eschema.type, rschema.type))
    kwargs.setdefault('help', rdef.description)
    if rschema.final:
        fieldclass = kwargs.pop('fieldclass', formfields.FIELDS[targetschema])
        if issubclass(fieldclass, formfields.StringField):
            if eschema.has_metadata(rschema, 'format'):
                # use RichTextField instead of StringField if the attribute has
                # a "format" metadata. But getting information from constraints
                # may be useful anyway...
                for cstr in rdef.constraints:
                    if isinstance(cstr, formfields.StaticVocabularyConstraint):
                        raise Exception('rich text field with static vocabulary')
                return formfields.RichTextField(**kwargs)
            # init StringField parameters according to constraints
            for cstr in rdef.constraints:
                if isinstance(cstr, formfields.StaticVocabularyConstraint):
                    kwargs.setdefault('choices', cstr.vocabulary)
                    break
            for cstr in rdef.constraints:
                if isinstance(cstr, formfields.SizeConstraint) and cstr.max is not None:
                    kwargs['max_length'] = cstr.max
            return fieldclass(**kwargs)
        if issubclass(fieldclass, formfields.FileField):
            if req:
                aff_kwargs = req.vreg['uicfg'].select('autoform_field_kwargs', req)
            else:
                aff_kwargs = formfields._AFF_KWARGS
            for metadata in formfields.KNOWN_METAATTRIBUTES:
                metaschema = eschema.has_metadata(rschema, metadata)
                if metaschema is not None:
                    metakwargs = aff_kwargs.etype_get(eschema, metaschema, 'subject')
                    kwargs['%s_field' % metadata] = formfields.guess_field(eschema, metaschema,
                                                                           req=req, **metakwargs)
        return fieldclass(**kwargs)
    return formfields.RelationField.fromcardinality(card, **kwargs)
