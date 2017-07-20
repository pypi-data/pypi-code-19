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
"""cubicweb-oaipmh entity's classes for OAI-PMH protocol"""
# TODO:  build the rql using syntax tree rather than string concatenation
# (using rqlquery?)


from abc import ABCMeta, abstractmethod

from isodate import datetime_isoformat

import rql
from cubicweb.view import EntityAdapter
from cubicweb.web.component import Component

from cubes.oaipmh import NoRecordsMatch, OAIError


def parse_setspec(setspec):
    """Split a setpec string and return <etype>, <relation>, <value> parts."""
    if not setspec:
        raise NoRecordsMatch('empty setspec')
    parts = setspec.split(':', 2)
    if len(parts) == 3:
        # setspec = etype:relation:value
        return parts
    elif len(parts) == 1:
        # setspec = etype
        return parts[0], None, None
    else:
        raise NoRecordsMatch('only handling one or three levels set specifiers')


def build_setspec(*specitems):
    """Build a setspec from individual specifier items."""
    return ':'.join(specitems)


class OAIComponent(Component):
    """OAI-PMH protocol component handling set specifiers listing and querying.
    """
    __regid__ = 'oai'
    # the manner in which the repository supports the notion of deleted
    # records (legitimate values are no ; transient ; persistent)
    deleted_handling = 'no'
    # maximum number of items for request returning a list of discrete items
    max_result_size = 20

    # Internals.
    __setspecs__ = {}
    __metadataformats__ = {}
    __setspecs_by_format__ = {}

    @classmethod
    def register(cls, specifier, formats):
        """Register a top-level set specifier."""
        cls.__setspecs__[specifier.setkey] = specifier
        for prefix, (fmt, _) in formats.iteritems():
            cls.__metadataformats__.setdefault(prefix, set([])).add(fmt)
            cls.__setspecs_by_format__.setdefault(prefix, set([])).add(specifier.setkey)

    def setspecs(self):
        """Yield known set specifier string values"""
        for specifier in self.__setspecs__.itervalues():
            for setkey, description in specifier.setspecs(self._cw):
                yield setkey, description
                for subkey, child in specifier.iteritems():
                    for value, description in child.setspecs(self._cw):
                        if value is not None:
                            yield build_setspec(setkey, subkey, value), description

    @classmethod
    def metadata_formats(cls):
        """Yield metadata formats (prefix, MetadataFormat) kwown by the
        component.
        """
        for prefix, formats in cls.__metadataformats__.iteritems():
            for fmt in formats:
                yield prefix, fmt

    def earliest_datestamp(self):
        """Return a datetime object guaranteed to be the lower limit of all
        datestamps recording changes, modifications, or deletions in the
        repository.

        This is used in the Identify verb (see
        http://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#Identify).
        """
        registered_etypes = [
            specifier.etype for specifier in self.__setspecs__.values()
            if isinstance(specifier, ETypeOAISetSpec)
        ]
        rset = self._cw.execute(
            'Any D LIMIT 1 WHERE X creation_date D, X is IN (%s)'
            % ', '.join(registered_etypes))
        if rset:
            return rset[0][0]
        # No entities of registered entity types exists in repository. Look
        # for an old object, 'system.version.cubicweb' CWProperty inserted at
        # instance creation.
        entity = self._cw.find('CWProperty', pkey=u'system.version.cubicweb').one()
        return entity.creation_date

    def match(self, setspec=None, from_date=None, until_date=None,
              metadata_prefix=None, from_eid=None):
        """Return a ResultSet or None and the eid of the next entity to yield.

        If `setspec` is not None and matches any of the adapter `setspecs`,
        the result set corresponding to this set restriction is returned. If
        `setspec` does not match any known setspecs, a NoRecordsMatch is raised.
        Finally, if `setspec` is None, a result set corresponding to all
        registered setspecs is returned.

        This result set has a size lower that class `max_result_size`
        attribute.

        The eid of the next entity to yield is returned (in case a result set
        is returned, None otherwise) if there are more results to fetch from
        the same query.
        """

        def add_dates_restrictions(specifier, query):
            """Extend `query` with from/until date restrictions."""
            if from_date is not None:
                query += ', X {0} >= %(from_date)s'.format(specifier.date_attr)
                args['from_date'] = from_date
            if until_date is not None:
                query += ', X {0} <= %(until_date)s'.format(specifier.date_attr)
                args['until_date'] = until_date
            return query

        qs = 'Any X ORDERBY X LIMIT {0}'.format(self.max_result_size + 1)
        where, args = [], {}
        # Add restriction from resumptionToken (from_eid).
        if from_eid is not None:
            where.append('X eid >= %(offset)s')
            args['offset'] = from_eid
        # Deal with setspec, if specified.
        if setspec is not None:
            etype, relation, value = parse_setspec(setspec)
            try:
                root = setspec = self.__setspecs__[etype]
            except KeyError:
                raise NoRecordsMatch('no setspec matching {0}'.format(etype))
            if (metadata_prefix is not None
                    and setspec.setkey not in self.__setspecs_by_format__.get(metadata_prefix, ())):
                msg = 'metadata prefix {0} not supported for set {1}'.format(
                    metadata_prefix, setspec.setkey)
                raise OAIError({'cannotDisseminateFormat': msg})
            if relation:
                try:
                    setspec = root[relation]
                except KeyError:
                    raise NoRecordsMatch('unregistered setspec {0}'.format(setspec))
            setspec_where, args_ = setspec.setspec_restrictions(value)
            setspec_where = add_dates_restrictions(root, setspec_where)
            where.append(setspec_where)
            args.update(args_)
            subquery = ''
        else:
            if metadata_prefix is not None:
                def specifiers():
                    try:
                        setkeys = self.__setspecs_by_format__[metadata_prefix]
                    except KeyError:
                        raise NoRecordsMatch('metadata prefix {0} not supported'.format(
                            metadata_prefix))
                    for setkey in setkeys:
                        yield self.__setspecs__[setkey]
            else:
                specifiers = self.__setspecs__.itervalues

            subqueries = []
            for specifier in specifiers():
                where_, args_ = specifier.setspec_restrictions()
                assert not args_, \
                    'unexpected "args" returned by `setspec_restrictions` from a top-level setspec'
                where_ = add_dates_restrictions(specifier, where_)
                subqueries.append('Any X WHERE ' + where_)
            subquery = ' UNION '.join('({0})'.format(qs) for qs in subqueries)
            # Add an identity restriction to work around
            # https://www.cubicweb.org/ticket/15393583 when there's something
            # in the WHERE clause already.
            where.append('X identity XX')
        # Final query.
        if where:
            qs += ' WHERE ' + ', '.join(where)
        if subquery:
            qs += ' WITH XX BEING ({0})'.format(subquery)
        rset = self._cw.execute(qs, args)
        return self.limit_rset(rset)

    def limit_rset(self, rset):
        """Return a result set limited to `max_result_size` along with the eid
        of next entity to be returned.
        """
        if len(rset) > self.max_result_size:
            next_eid = str(rset[-1][0])
            rset = rset.limit(self.max_result_size, inplace=True)
        else:
            next_eid = None
        return rset, next_eid

    def match_identifier(self, identifier):
        """Return a result set matching identifier."""
        results = []
        for spec in self.__setspecs__.itervalues():
            qs, args = spec.query_for_identifier(unicode(identifier))
            try:
                rset = self._cw.execute(qs, args)
            except rql.TypeResolverException:
                # Probably no matching entity of target type with specified
                # identifier (may occur if several adapters share the same
                # identifier type, e.g. eid).
                continue
            if rset:
                assert not results, \
                    'ambiguous result for identifier {0}'.format(identifier)
                results.append(rset)
        return results[0] if results else self._cw.empty_rset()


class OAIPMHRecordAdapter(EntityAdapter):
    """Entity adapter representing an OAI-PMH record.

    Concret adapter are implemented for one entity type and define a top-level
    specifier to be returned by `set_definition` method.
    """
    __regid__ = 'IOAIPMHRecord'
    __abstract__ = True
    # the name of the attribute to be used as OAI identifier
    identifier_attribute = 'eid'
    # metadata formats available for the adapted entity, should be a mapping
    # from prefix to (format, vid) tuple where `format` in an instance of
    # MetadataFormat.
    metadata_formats = None
    # date attribute to filter results by from/until request parameters
    date_attr = 'modification_date'
    # indicate that the record got deleted
    deleted = False

    @classmethod
    def __registered__(cls, *args):
        specifier = cls.set_definition()
        if specifier is not None:
            formats = cls.metadata_formats
            OAIComponent.register(specifier, formats)
        return super(OAIPMHRecordAdapter, cls).__registered__(*args)

    @classmethod
    def set_definition(cls):
        """Return the top-level set specifier for adapter entity type.

        May return None if the adapter should not be registered within
        `OAIComponent`, e.g., if it is only used to build a record from an
        entity queried by its identifier not by a setspec.
        """
        return None

    @property
    def identifier(self):
        """OAI-PMH identifier for adapted entity."""
        return unicode(getattr(self.entity, self.identifier_attribute))

    @property
    def date(self):
        """OAI-PMH date information for adapted entity."""
        return getattr(self.entity, self.date_attr)

    @property
    def datestamp(self):
        """String representation of OAI-PMH date information for adapted entity.
        """
        return datetime_isoformat(self.date)

    def metadata(self, prefix):
        """Return an XML-formatted representation of adapted entity."""
        try:
            _, vid = self.metadata_formats[prefix]
        except KeyError:
            raise NoRecordsMatch('unsupported metadata prefix "{0}"'.format(prefix))
        data = self._cw.view(vid, w=None, rset=self.entity.as_rset())
        if isinstance(data, unicode):
            # Underlying view may be 'binary' or not.
            data = data.encode('utf-8')
        return data


class OAISetSpec(object):
    """Base class for an OAI-PMH request set specifier."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def setspecs(self, cnx):
        """Yield setspec strings associated with this entry in the the setspec
        hierarchy.
        """

    @abstractmethod
    def setspec_restrictions(self, value=None):
        """Return the WHERE part of the RQL query string and a dict of query
        parameters for this set specifier.
        """


class ETypeOAISetSpec(OAISetSpec, dict):
    """OAI-PMH set specifier matching an entity type."""

    def __init__(self, etype, identifier_attribute, setkey=None,
                 date_attr=OAIPMHRecordAdapter.date_attr):
        """Build a top-level set specifier."""
        super(ETypeOAISetSpec, self).__init__()
        if setkey is None:
            setkey = etype.lower()
        self.etype = etype
        self.identifier_attribute = identifier_attribute
        self.setkey = setkey
        self.date_attr = date_attr

    def __str__(self):
        return '{0.__class__.__name__} "{0.setkey}" {1}'.format(
            self, super(ETypeOAISetSpec, self).__str__())

    def __setitem__(self, subset, specifier):
        """Register a new `OAISetSpec` as child of this object."""
        super(ETypeOAISetSpec, self).__setitem__(subset, specifier)
        specifier.__parent__ = self

    def setspecs(self, cnx):
        yield self.setkey, cnx._(self.etype)

    def setspec_restrictions(self, value=None):
        if value is not None:
            raise NoRecordsMatch('unexpected setspec')
        return 'X is ' + self.etype, {}

    def query_for_identifier(self, identifier):
        """Return an RQL query string and a dict of query parameter for given
        `identifier` within the context of this set specifier.
        """
        if self.identifier_attribute == 'eid':
            try:
                identifier = int(identifier)  # XXX
            except ValueError:
                pass
        qs = 'Any X WHERE X is {etype}, X {attr} %(identifier)s'.format(
            etype=self.etype, attr=self.identifier_attribute)
        return qs, {'identifier': identifier}


class RelatedEntityOAISetSpec(OAISetSpec):
    """OAI-PMH second-level set specifier to match on a relation on the
    top-level entry.
    """

    def __init__(self, rtype, targettype, targetattr,
                 description=None, exclude=(), role='subject'):
        self.rtype = rtype
        if role not in ('subject', 'object'):
            raise ValueError('invalid role {}'.format(role))
        self.role = role
        self.targettype = targettype
        self.targetattr = targetattr
        self.description = description
        self.exclude = exclude
        self.__parent__ = None

    def setspecs(self, cnx):
        qs = 'DISTINCT String N WHERE X is {etype}, X {attr} N'
        if self.exclude:
            if len(self.exclude) > 1:
                qs += ', NOT X {{attr}} IN ({0})'.format(
                    ','.join(map(repr, self.exclude)))  # pylint: disable=bad-builtin
            else:
                qs += ', NOT X {{attr}} "{0}"'.format(
                    self.exclude[0])
        rset = cnx.execute(qs.format(
            etype=self.targettype, attr=self.targetattr))
        for value, in rset.rows:
            desc = self.description.format(value) if self.description else u''
            yield value, desc

    def setspec_restrictions(self, value):
        baseqs, args = self.__parent__.setspec_restrictions()
        if self.role == 'subject':
            subqs = 'X {rtype} Y'
        else:
            subqs = 'Y {rtype} X'
        subqs = (subqs + ', Y {attrname} %(value)s').format(
            rtype=self.rtype, attrname=self.targetattr)
        qs = ', '.join([baseqs, subqs])
        args['value'] = unicode(value)
        return qs, args
