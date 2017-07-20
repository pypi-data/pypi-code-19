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
"""cubicweb-oaipmh tests"""
from __future__ import print_function

from datetime import date, timedelta
from functools import wraps
import time
import unittest2

from isodate import datetime_isoformat
from dateutil.parser import parse as parse_date
from lxml import etree
import pytz
from six import text_type

from logilab.common import tempattr

from cubicweb.devtools.testlib import CubicWebTC
from cubicweb.pyramid.test import PyramidCWTest

from cubes.oaipmh import utcnow, MetadataFormat, ResumptionToken
from cubes.oaipmh.entities import OAIComponent, NoRecordsMatch
from cubes.oaipmh.views import OAIError, OAIRequest


def agent(cnx, name=None, kind=u'person', **kwargs):
    return cnx.create_entity('Agent', name=name,
                             kind=cnx.create_entity('AgentKind', name=kind),
                             **kwargs)


def xmlview_snippet(cnx, eid):
    """Return a snippet of xmlitem view for entity with `eid`."""
    entity = cnx.entity_from_eid(eid)
    return u'<%s eid="%s" cwuri="%s"' % (entity.cw_etype, entity.eid,
                                         entity.cwuri)


class ResumptionTokenTC(unittest2.TestCase):

    def test_none(self):
        token = ResumptionToken.parse(None)
        self.assertIsNone(token.eid)
        self.assertFalse(token)
        self.assertIsNone(token.encode())

    def test_unicode(self):
        """Make sure we can parse unicode string."""
        token = ResumptionToken(1, metadata_prefix='oai_dc')
        utoken = text_type(token.encode())
        self.assertEqual(ResumptionToken.parse(utoken), token)

    def test_roundtrip(self):
        attrs = ('eid', 'setspec', 'from_date', 'until_date', 'metadata_prefix')
        for tokeninfo in [
            (1, ),  # All none.
            (6, 'pif', '2016-07-31T22:00:00Z', '2016-09-14T13:39:03Z', 'oai_dc'),
            (8, 'paf', None, '2016-09-14T13:39:03Z', 'myfmt'),
        ]:
            params = dict(zip(attrs, tokeninfo))
            with self.subTest(**params):
                token = ResumptionToken(**params)
                encoded = token.encode()
                self.assertEqual(ResumptionToken.parse(encoded), token)


class OAITestMixin(object):

    def oai_component(self, cnx):
        """Return the "oai" component"""
        return self.vreg['components'].select('oai', cnx)


class OAIComponentTC(CubicWebTC, OAITestMixin):

    def test_registered(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            setspecs = oai.__setspecs__
            self.assertCountEqual(setspecs.keys(),
                                  ['agent', 'activity', 'thing'])
            self.assertCountEqual(setspecs['agent'].keys(),
                                  ['kind', 'involved_in'])
            self.assertCountEqual(setspecs['activity'].keys(),
                                  ['associated_with'])
            self.assertCountEqual(setspecs['thing'].keys(), [])

    def test_match(self):
        with self.admin_access.repo_cnx() as cnx:
            oai = self.oai_component(cnx)
            with self.assertRaises(NoRecordsMatch) as cm:
                oai.match(u'cwuser')
            self.assertEqual(cm.exception.errors,
                             {'noRecordsMatch': 'no setspec matching cwuser'})

    def test_setspecs(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Activity', name=u'hacking')
            bob = agent(cnx, u'bob')
            cnx.commit()
            expected = (
                'agent',
                'agent:kind:person',
                'agent:involved_in:hacking',
                'activity', 'activity:associated_with:%s' % bob.name,
                'thing',
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)

    def test_setspecs_no_identifier_attribute(self):
        """An entity without an "identifier_attribute" set should not yield a
        setspec for related entities.
        """
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx)
            cnx.commit()
            expected = (
                'agent',
                'agent:kind:person',
                'activity',
                'thing',
            )
            oai = self.oai_component(cnx)
            setspecs = [x[0] for x in oai.setspecs()]
            self.assertCountEqual(setspecs, expected)

    def test_metadata_formats(self):
        with self.admin_access.cnx() as cnx:
            oai = self.oai_component(cnx)
            formats = dict(oai.metadata_formats())
            expected = {
                'oai_dc': MetadataFormat(
                    'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                    'http://www.openarchives.org/OAI/2.0/oai_dc/'),
                'eac_cpf': MetadataFormat(
                    'http://eac.staatsbibliothek-berlin.de/schema/cpf.xsd',
                    'urn:isbn:1-931666-33-4'),
            }
            self.assertEqual(formats, expected)


class OAIRequestTC(CubicWebTC):

    def test_rset(self):
        """Test `rset` function for exceptions."""
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, u'bob')
            agent(cnx, u'New York City', kind=u'authority')
            cnx.commit()
        with self.admin_access.web_request() as req:
            for setspec, msg in [
                ('agent:zen', 'only handling one or three levels set specifiers'),
                ('agent:kind:family', (
                    'The combination of the values of the from, until, and '
                    'set arguments results in an empty list.')),
                ('scregneugneu', 'no setspec matching scregneugneu'),
            ]:
                oairq = OAIRequest('http://testing.fr', setspec=setspec)
                with self.assertRaises(OAIError) as cm:
                    oairq.rset(req)
                self.assertEqual(cm.exception.errors, {'noRecordsMatch': msg})

    def test_rset_token(self):
        with self.admin_access.repo_cnx() as cnx:
            agent(cnx, u'bob')
            simpsons = agent(cnx, u'The Simpson', kind=u'family')
            cnx.commit()

        def oairq(**kwargs):
            return OAIRequest('http://testing.fr', setspec='agent', **kwargs)

        with self.admin_access.web_request() as req:
            with tempattr(OAIComponent, 'max_result_size', 1):
                rset, next_eid = oairq().rset(req)
                self.assertEqual(len(rset), 1)
                self.assertEqual(next_eid, str(simpsons.eid))
                token = ResumptionToken(next_eid).encode()
                rset, next_eid = oairq(resumption_token=token).rset(req)
                self.assertEqual(len(rset), 1)
                self.assertIsNone(next_eid)
            # All results are returned, the resumptionToken is None.
            rset, next_eid = oairq().rset(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(next_eid)
            # and this, even if the user specified an input token.
            token = ResumptionToken(1).encode()
            rset, next_eid = oairq(resumption_token=token).rset(req)
            self.assertEqual(len(rset), 2)
            self.assertIsNone(next_eid)

    def test_to_xml(self):
        oairq = OAIRequest('http://testing.fr', verb='GetRecord',
                           identifier='abc', metadata_prefix='oai_dc')
        xml = oairq.to_xml()
        expected = {
            'verb': 'GetRecord',
            'metadataPrefix': 'oai_dc',
            'identifier': 'abc',
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_with_dates(self):
        datestr = '2016-09-23T12:34:44Z'
        oairq = OAIRequest('http://testing.fr', verb='ListIdentifiers',
                           from_date=datestr, until_date=None)
        xml = oairq.to_xml()
        expected = {
            'verb': 'ListIdentifiers',
            'from': '2016-09-23T12:34:44Z',
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_with_token(self):
        token = ResumptionToken(7)
        oairq = OAIRequest('http://testing.fr', verb='ListIdentifiers',
                           resumption_token=token.encode())
        xml = oairq.to_xml()
        expected = {
            'verb': 'ListIdentifiers',
            'resumptionToken': token.encode(),
        }
        self.assertEqual(xml.attrib, expected)

    def test_to_xml_errors(self):
        oairq = OAIRequest('http://testing.fr', verb='ListIdentifiers',
                           metadata_prefix='qwerty')
        xml = oairq.to_xml(errors='yes')
        self.assertEqual(xml.attrib, {})


def no_validate_xml(method):
    """Disable XML schema validation, often because the underlying metadata
    part of the response (RDF, XSD) is not validable (or we don't know how to
    do it).
    """
    @wraps(method)
    def wrapper(self):
        self._validate_xml = False
        self._debug_xml = True
        return method(self)
    return wrapper


def xmlpp(string):
    """Parse and pretty-print XML data from `string`."""
    print(etree.tostring(etree.fromstring(string), pretty_print=True))


class OAIPMHViewsTC(PyramidCWTest, OAITestMixin):
    settings = {
        # to get clean traceback in tests (instead of in an html error page)
        'cubicweb.bwcompat': False,
        # avoid noise in test output (UserWarning: !! WARNING WARNING !! you
        # should stop this instance)
        'cubicweb.session.secret': 'x',
        'cubicweb.auth.authtkt.session.secret': 'x',
        'cubicweb.auth.authtkt.persistent.secret': 'x',
    }

    _validate_xml = True
    _debug_xml = True

    def assertXmlValid(self, xml_data, xsd_filename, debug=False):
        """Validate an XML file (.xml) according to an XML schema (.xsd)."""
        with open(xsd_filename) as xsd:
            xmlschema = etree.XMLSchema(etree.parse(xsd))
        # Pretty-print xml_data to get meaningfull line information.
        xml_data = etree.tostring(etree.fromstring(xml_data), pretty_print=True)
        root = etree.fromstring(xml_data)
        if debug and not xmlschema.validate(root):
            print(xml_data)
        xmlschema.assertValid(root)

    def oai_request(self, req, **formparams):
        response = self.webapp.get('/oai', formparams)
        self.assertEqual(response.headers['Content-Type'], 'text/xml; charset=UTF-8')
        if self._validate_xml:
            self.assertXmlValid(response.body, self.datapath('OAI-PMH.xsd'),
                                debug=self._debug_xml)
        return response.body

    def test_xml_attributes_and_namespaces(self):
        """Check XML attributes and namespace declaration of the response."""
        with self.admin_access.web_request() as req:
            # simple request, generating an error but enough to get a properly
            # formatter response.
            result = self.oai_request(req)
            xml = etree.fromstring(result)
            nsmap = {None: 'http://www.openarchives.org/OAI/2.0/',
                     'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
            self.assertEqual(xml.nsmap, nsmap)
            attrib = {
                '{http://www.w3.org/2001/XMLSchema-instance}schemaLocation': ' '.join(
                    ['http://www.openarchives.org/OAI/2.0/',
                     'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd']),
            }
            self.assertEqual(xml.attrib, attrib)

    def test_responsedate(self):
        """Check <responseDate>"""
        with self.admin_access.web_request() as req:
            # Simple request, generating an error but enough to get a properly
            # formatter response.
            now = utcnow()
            result = self.oai_request(req)
        # Check tzinfo abbreviation is present (Z for UTC).
        pattern = '<responseDate>{0}</responseDate>'.format(
            datetime_isoformat(now))
        self.assertIn(pattern, result)

    def test_noverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req)
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">no verb specified</error',
                      result)

    def test_badverb(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='coucou')
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        self.assertIn('<error code="badVerb">illegal verb "coucou"</error>',
                      result)

    def test_identify(self):
        self.config.global_set_option('admin-email', 'oai-admin@example.org')
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='Identify')
            cwversion = req.find(
                'CWProperty', pkey='system.version.cubicweb').one()
            earliest_datestamp = datetime_isoformat(cwversion.creation_date)
        self.assertIn('<repositoryName>unset title</repositoryName>', result)
        self.assertIn('<baseURL>https://localhost:80/oai</baseURL>', result)
        self.assertIn('<protocolVersion>2.0</protocolVersion>', result)
        self.assertIn('<adminEmail>oai-admin@example.org</adminEmail>', result)
        self.assertIn(
            '<earliestDatestamp>{}</earliestDatestamp>'.format(earliest_datestamp),
            result)
        self.assertIn('<deletedRecord>no', result)
        self.assertIn('<granularity>YYYY-MM-DDThh:mm:ssZ', result)
        with self.admin_access.cnx() as cnx:
            entity = cnx.create_entity('Thing', identifier=u'123')
            cnx.commit()
            earliest_datestamp = datetime_isoformat(entity.creation_date)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='Identify')
        self.assertIn(
            '<earliestDatestamp>{}</earliestDatestamp>'.format(earliest_datestamp),
            result)

    def test_identify_badargument(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='Identify', set='plouf')
        self.assertIn(
            '<error code="badArgument">Identify accepts no argument</error',
            result)

    def test_listmetadaformats(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListMetadataFormats')
        self.assertIn('<metadataPrefix>oai_dc</metadataPrefix>', result)
        self.assertIn('<metadataPrefix>eac_cpf</metadataPrefix>', result)

    def test_listmetadaformats_iddoesnotexist(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListMetadataFormats',
                                      identifier='-123')
        self.assertIn('<error code="idDoesNotExist">', result)

    def test_listmetadaformats_by_identifier(self):
        with self.admin_access.cnx() as cnx:
            agent_eid = agent(cnx, u'bob').eid
            cnx.create_entity('Thing', identifier=u'123')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListMetadataFormats',
                                      identifier=str(agent_eid))
        self.assertIn('<metadataPrefix>oai_dc</metadataPrefix>', result)
        self.assertIn('<metadataPrefix>eac_cpf</metadataPrefix>', result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListMetadataFormats',
                                      identifier='123')
        self.assertIn('<metadataPrefix>oai_dc</metadataPrefix>', result)
        self.assertNotIn('<metadataPrefix>eac_cpf</metadataPrefix>', result)

    def test_listsets(self):
        with self.admin_access.cnx() as cnx:
            agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListSets')
        self.assertIn('<request verb="ListSets">https://localhost:80/oai</request>',
                      result)
        for spec in ('agent', 'activity'):
            self.assertIn('<setSpec>{0}</setSpec>'.format(spec),
                          result)
        self.assertIn(('<setSpec>agent:kind:person</setSpec>'
                       '<setName>An agent of kind person</setName>'),
                      result)
        self.assertIn(('<setSpec>activity:associated_with:bob</setSpec>'
                       '<setName>Agent bob\'s activities</setName>'),
                      result)

    def test_listidentifiers_no_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers')
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        self.assertIn(('<error code="badArgument">'
                       'ListIdentifiers verb requires a "metadataPrefix" restriction'
                       '</error>'),
                      result)

    def test_listidentifiers_setspect_bad_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent',
                                      metadataPrefix='unexisting')
        self.assertIn('<request',
                      result)
        self.assertIn(('<error code="cannotDisseminateFormat">'
                       'metadata prefix unexisting not supported for set agent'
                       '</error>'),
                      result)

    def test_resumptiontoken_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            bob = agent(cnx, u'bob')
            cnx.commit()

        def check_request(expected_identifiers, token=None):
            with self.admin_access.web_request() as req:
                kwargs = {'resumptionToken': token} if token is not None else {}
                result = self.oai_request(
                    req, verb='ListIdentifiers', set='agent',
                    metadataPrefix='oai_dc', **kwargs)
                # Ensure there are as many <identifier> tag than expected items.
                self.assertEqual(
                    result.count('<identifier>'), len(expected_identifiers))
                for identifier in expected_identifiers:
                    self.assertIn(
                        '<identifier>{0}</identifier>'.format(identifier), result)
                return result

        result = check_request([alice.eid, bob.eid])
        # All results returned, no resumptionToken is request -> no
        # resumptionToken in response.
        self.assertNotIn('resumptionToken', result)
        with tempattr(OAIComponent, 'max_result_size', 1):
            result = check_request([alice.eid])
            root = etree.fromstring(result)
            token = root.find('.//{%s}resumptionToken' % root.nsmap[None])
            date = parse_date(token.attrib['expirationDate'])
            self.assertLess(utcnow() + timedelta(hours=1) - date,
                            timedelta(seconds=1))
            expected_token = ResumptionToken(bob.eid, setspec='agent',
                                             metadata_prefix='oai_dc')
            self.assertEqual(token.text, expected_token.encode())
            result = check_request([bob.eid], token=expected_token.encode())
            # No more results -> empty resumptionToken.
            self.assertIn('<resumptionToken/>', result)
            # Empty result, probably a badResumptionToken.
            new_token = ResumptionToken(bob.eid + 1)
            result = check_request([], token=new_token.encode())
            self.assertIn('badResumptionToken', result)

    def test_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice').eid
            newyork = agent(cnx, u'New York City', u'authority').eid
            cnx.create_entity('Thing', identifier=u'007')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      metadataPrefix='oai_dc')
            self.assertIn('<identifier>{0}</identifier>'.format(newyork), result)
            self.assertIn('<identifier>{0}</identifier>'.format(alice), result)
            self.assertIn('<identifier>007</identifier>', result)
            self.assertEqual(result.count('<identifier>'), 3)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      metadataPrefix='eac_cpf')
            self.assertIn('<identifier>{0}</identifier>'.format(newyork), result)
            self.assertIn('<identifier>{0}</identifier>'.format(alice), result)
            self.assertNotIn('<identifier>007</identifier>', result)
            self.assertEqual(result.count('<identifier>'), 2)

    def test_listidentifiers_setspec(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice').eid
            newyork = agent(cnx, u'New York City', u'authority').eid
            cnx.create_entity('Thing', identifier=u'007')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc')
            self.assertIn('<identifier>{0}</identifier>'.format(newyork), result)
            self.assertIn('<identifier>{0}</identifier>'.format(alice), result)
            self.assertEqual(result.count('<identifier>'), 2)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      metadataPrefix='oai_dc',
                                      set='agent:kind:person')
            self.assertIn('<identifier>{0}</identifier>'.format(alice),
                          result)
            self.assertNotIn('<identifier>{0}</identifier>'.format(newyork),
                             result)
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='activity', metadataPrefix='oai_dc')
            self.assertIn('<error code="noRecordsMatch">', result)
            result = self.oai_request(req, verb='ListIdentifiers', set='thing',
                                      metadataPrefix='oai_dc')
            self.assertIn('<identifier>007</identifier>', result)

    def test_listidentifiers_deleted(self):
        """Check <header> element (status attribute, datestamp) for deleted
        records in ListIdentifiers response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'a')
            deleted = cnx.create_entity('Thing', identifier=u'b')
            date_before = deleted.modification_date.replace(tzinfo=pytz.utc)
            cnx.commit()
            time.sleep(1)
            deleted.cw_set(deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='thing',
                                      metadataPrefix='oai_dc')
            self.assertIn('<identifier>a</identifier>', result)
            self.assertIn('<header status="deleted">', result)
            root = etree.fromstring(result)
            ns = root.nsmap[None]
            # only one <header status="..."> element
            header, = root.findall('.//{%s}header[@status]' % ns)
            datestamp = header.find('{%s}datestamp' % ns).text
            date = parse_date(datestamp)
            self.assertGreater(date, date_before.replace(microsecond=0))

    def test_listrecords_noargument(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords')
        self.assertIn('<request>https://localhost:80/oai</request>',
                      result)
        expected = (
            '<error code="badArgument">'
            'ListRecords verb requires a "metadataPrefix" restriction'
            '</error>'
        )
        self.assertIn(expected, result)

    @no_validate_xml
    def test_listrecords(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            newyork = agent(cnx, u'New York', kind=u'authority')
            cnx.create_entity('Thing', identifier=u'a')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', metadataPrefix='oai_dc')
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertIn(str(newyork.eid), result)
            self.assertIn('<identifier>a</identifier>', result)

    @no_validate_xml
    def test_listrecords_resumptiontoken(self):
        """ListRecords without set restriction, checking resumptionToken."""
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            newyork = agent(cnx, u'New York', kind=u'authority')
            cnx.create_entity('Thing', identifier=u'a')
            cnx.commit()
        expected_token = ResumptionToken(newyork.eid, metadata_prefix='oai_dc')
        with self.admin_access.web_request() as req:
            with tempattr(OAIComponent, 'max_result_size', 1):
                result = self.oai_request(req, verb='ListRecords',
                                          metadataPrefix='oai_dc')
                self.assertIn(xmlview_snippet(req, alice.eid), result)
                self.assertNotIn(
                    '<identifier>{0}</identifier>'.format(newyork.eid), result)
                self.assertNotIn('<identifier>a</identifier>', result)
                self.assertIn(
                    '{0}</resumptionToken>'.format(expected_token.encode()),
                    result)
            result = self.oai_request(req, verb='ListRecords',
                                      metadataPrefix='oai_dc',
                                      resumptionToken=expected_token.encode())
            self.assertIn(
                '<identifier>{0}</identifier>'.format(newyork.eid), result)
            self.assertIn('<identifier>a</identifier>', result)
            # The response completes a prior response, we get an empty
            # resumptionToken.
            self.assertIn('<resumptionToken/>', result)

    @no_validate_xml
    def test_listrecords_resumptiontoken_no_metadataprefix(self):
        """ListRecords with resumptionToken but *no metadataPrefix*."""
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            newyork = agent(cnx, u'New York', kind=u'authority')
            cnx.create_entity('Thing', identifier=u'a')
            cnx.commit()
        # The expected ResumptionToken built from request parameters.
        token = ResumptionToken(newyork.eid, metadata_prefix='oai_dc')
        with self.admin_access.web_request() as req:
            with tempattr(OAIComponent, 'max_result_size', 1):
                # First request includes metadataPrefix.
                result = self.oai_request(req, verb='ListRecords',
                                          metadataPrefix='oai_dc')
                self.assertIn(xmlview_snippet(req, alice.eid), result)
                self.assertNotIn(
                    '<identifier>{0}</identifier>'.format(newyork.eid), result)
                self.assertNotIn('<identifier>a</identifier>', result)
                self.assertIn(
                    '{0}</resumptionToken>'.format(token.encode()),
                    result)
            # Second request has no metadataPrefix but has resumptionToken,
            # from which metadataPrefix will be fetched.
            result = self.oai_request(req, verb='ListRecords',
                                      resumptionToken=token.encode())
            self.assertIn(
                '<identifier>{0}</identifier>'.format(newyork.eid), result)
            self.assertIn('<identifier>a</identifier>', result)
            # The response completes a prior response, we get an empty
            # resumptionToken.
            self.assertIn('<resumptionToken/>', result)

    @no_validate_xml
    def test_listrecords_filter_metadata_prefix(self):
        """Make sure records that do not match requests metadataPrefix are not
        listed.
        """
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            cnx.create_entity('Thing', identifier=u'a')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords',
                                      metadataPrefix='eac_cpf')
            self.assertIn('<identifier>{0}</identifier>'.format(alice.eid),
                          result)
            self.assertNotIn('<identifier>a</identifier>', result)

        # Make sure records not matching metadataPrefix have no effect on
        # result set (eg. do not modify resumptionToken).
        with self.admin_access.cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.commit()
        with tempattr(OAIComponent, 'max_result_size', 2):
            with self.admin_access.web_request() as req:
                result = self.oai_request(req, verb='ListRecords',
                                          metadataPrefix='eac_cpf')
                self.assertIn('<identifier>{0}</identifier>'.format(alice.eid),
                              result)
                self.assertIn('<identifier>{0}</identifier>'.format(bob.eid),
                              result)
                self.assertNotIn('resumptionToken', result)

    @no_validate_xml
    def test_listrecords_filter_metadata_prefix_no_result(self):
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'a')
            cnx.create_entity('Thing', identifier=u'b')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords',
                                      metadataPrefix='eac_cpf')
            self.assertIn('noRecordsMatch', result)
            self.assertNotIn('<identifier>', result)

    @no_validate_xml
    def test_listrecords_with_set(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            newyork = agent(cnx, u'New York', kind=u'authority')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='agent',
                                      metadataPrefix='oai_dc')
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertIn(str(newyork.eid), result)
            result = self.oai_request(req, verb='ListRecords',
                                      set='agent:kind:person',
                                      metadataPrefix='oai_dc')
            self.assertIn(xmlview_snippet(req, alice.eid), result)
            self.assertNotIn(str(newyork.eid), result)

    @no_validate_xml
    def test_listrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in ListRecords response.
        """
        with self.admin_access.cnx() as cnx:
            thing = cnx.create_entity('Thing', identifier=u'a')
            deleted = cnx.create_entity('Thing', identifier=u'b',
                                        deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListRecords', set='thing',
                                      metadataPrefix='oai_dc')
            self.assertNotIn(xmlview_snippet(req, deleted.eid),
                             result)
            # but record present
            self.assertIn('<identifier>b</identifier>', result)
            # not-deleted thing is present with metadata.
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    def test_getrecord_missing_identifier(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      metadataPrefix='oai_dc')
        self.assertIn(('<error code="badArgument">GetRecord verb requires '
                       '"identifier" restriction'), result)

    def test_getrecord_missing_metadataprefix(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier='doesnotmatter')
        self.assertIn(('<error code="badArgument">GetRecord verb requires '
                       '"metadataPrefix" restriction'), result)

    @no_validate_xml
    def test_getrecord(self):
        with self.admin_access.repo_cnx() as cnx:
            thing = cnx.create_entity('Thing', identifier=u'aaa')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=u'aaa', metadataPrefix='oai_dc')
            self.assertIn(xmlview_snippet(req, thing.eid), result)

    @no_validate_xml
    def test_getrecord_agent(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=str(bob.eid),
                                      metadataPrefix='oai_dc')
        self.assertIn(u'<metadata><Agent eid="{0}"'.format(bob.eid), result)
        self.assertIn(u'bob', result)

    @no_validate_xml
    def test_getrecord_agent_other_prefix(self):
        with self.admin_access.repo_cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=str(bob.eid),
                                      metadataPrefix='eac_cpf')
        expected = (
            u'<metadata>'
            u'<eac-cpf xmlns:xlink="http://www.w3.org/1999/xlink"'
            u' xmlns="urn:isbn:1-931666-33-4">'
            u'<control><recordId/>{0}</control></eac-cpf>'.format(bob.eid)
        )
        self.assertIn(expected, result)

    def test_getrecord_unsupported_metadataprefix(self):
        with self.admin_access.repo_cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'aaa')
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord',
                                      identifier=u'aaa',
                                      metadataPrefix='ahah')
        expected = u'<error code="noRecordsMatch">unsupported metadata prefix "ahah"</error>'
        self.assertIn(expected, result)

    def test_getrecord_deleted(self):
        """Check absence of <metadata> or <about> elements for deleted
        records in GetRecord response.
        """
        with self.admin_access.cnx() as cnx:
            cnx.create_entity('Thing', identifier=u'd', deleted=True)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier=u'd',
                                      metadataPrefix='oai_dc')
            # record is present
            self.assertIn('<identifier>d</identifier>', result)
            # but not data
            self.assertNotIn('<metadata>', result)
            self.assertNotIn('<Thing', result)

    def test_getrecord_inexistant(self):
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='GetRecord', identifier=u'z',
                                      metadataPrefix='doesnotmatter')
            self.assertIn('idDoesNotExist', result)

    def test_from_until_error(self):
        with self.admin_access.web_request() as req:
            dates = {'from': date(2013, 1, 2).isoformat(),
                     'until': date(2011, 1, 2).isoformat()}
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc', **dates)
            self.assertIn('<error code="badArgument">the from argument', result)

    def test_from_until_listidentifiers(self):
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            bob = agent(cnx, u'bob')
            cnx.commit()
        with self.admin_access.repo_cnx() as cnx:
            alice_date = cnx.entity_from_eid(alice.eid).modification_date
            bob_date = alice_date + timedelta(seconds=2)
            cnx.entity_from_eid(bob.eid).cw_set(modification_date=bob_date)
            cnx.commit()
        in_between_date = datetime_isoformat(alice_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc',
                                      **{'from': in_between_date})
            self.assertIn(str(bob.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc',
                                      **{'until': in_between_date})
            self.assertNotIn(str(bob.eid), result)
            self.assertIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(str(bob.eid), result)
            self.assertIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers', set='agent',
                                      metadataPrefix='oai_dc',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)

    def test_from_until_listidentifiers_setspec(self):
        """Check from/until restriction with a multi-level setspec
        `agent:kind:family`
        """
        with self.admin_access.cnx() as cnx:
            alice = agent(cnx, u'alice')
            simpsons = agent(cnx, u'The Simpson', u'family')
            adams = agent(cnx, u'Adams family', u'family')
            cnx.commit()
        with self.admin_access.cnx() as cnx:
            simpsons_date = cnx.entity_from_eid(simpsons.eid).modification_date
            adams = cnx.entity_from_eid(adams.eid)
            adams_date = simpsons_date + timedelta(seconds=2)
            adams.cw_set(modification_date=adams_date)
            cnx.commit()
        in_between_date = datetime_isoformat(
            simpsons_date + timedelta(seconds=1))
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      metadataPrefix='oai_dc',
                                      **{'from': in_between_date})
            self.assertNotIn(str(simpsons.eid), result)
            self.assertIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      metadataPrefix='oai_dc',
                                      **{'until': in_between_date})
            self.assertIn(str(simpsons.eid), result)
            self.assertNotIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      metadataPrefix='oai_dc',
                                      **{'from': '1970-12-1',
                                         'until': '2099-01-02'})
            self.assertIn(str(simpsons.eid), result)
            self.assertIn(str(adams.eid), result)
            self.assertNotIn(str(alice.eid), result)
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:kind:family',
                                      metadataPrefix='oai_dc',
                                      **{'until': '1970-12-31'})
            self.assertIn('<error code="noRecordsMatch">The combi', result)

    def test_related_setspec_role_object(self):
        with self.admin_access.cnx() as cnx:
            bob = agent(cnx, u'bob')
            cnx.create_entity('Activity', name=u'hacking',
                              associated_with=bob)
            cnx.commit()
        with self.admin_access.web_request() as req:
            result = self.oai_request(req, verb='ListIdentifiers',
                                      set='agent:involved_in:hacking',
                                      metadataPrefix='oai_dc')
            self.assertIn('<identifier>{}</identifier>'.format(bob.eid),
                          result)


if __name__ == '__main__':
    import unittest
    unittest.main()
