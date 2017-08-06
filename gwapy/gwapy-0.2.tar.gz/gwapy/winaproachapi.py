import os.path
import re
import xml.dom.minidom as minidom

from suds.client import Client

from incidentrecord import IncidentRecord

# Documentation about the xml fields
# http://aproachwstest.muc.amadeus.net:18080/aproachwebservicehelp/jsps/fields.jsp

# PRD URL
WP_WSDL = 'http://aproach.muc.amadeus.net/aproach/services/AproachWebServices?WSDL'
# PPT URL
PPT_WP_WSDL = 'http://aproachwstest.muc.amadeus.net:8095/aproach/services/AproachWebServices?WSDL'


class WinAproachApi:
    def __init__(self, phase='PRD'):
        self.login, password = open(os.path.expanduser('~/.winpwd')).read().split()
        self._wpUrl = WP_WSDL
        if 'PRD' not in phase.upper():
            self._wpUrl = PPT_WP_WSDL
        self._wpclient = Client(self._wpUrl, username=self.login, password=password)
        self.objectMapping = {
            'IR': IncidentRecord
        }

    def update_ir_description(self, ir_id, description_string):
        strRec = ('<record id=\"%s\" type=\"IR\" database=\"prd\"><fft sword=\"S0E01\" name=\"Description\">'
                  '<line>%s</line></fft></record>' % (
                      ir_id, description_string))
        return self._wpclient.service.update(strRec)

    def retrieve(self, record_number):
        xml_string = self._wpclient.service.retrieve(record_number)
        dom = minidom.parseString(xml_string)
        xml_record = dom.getElementsByTagName('record')[0]
        record_type = xml_record.attributes['type'].value
        record = self.objectMapping[record_type]()
        record.recordID(xml_record.attributes['id'].value)
        record.parseXml(xml_string)
        return record

    def search(self, recType, title, startDate, endDate):
        title = re.sub("[/:-]", " ", title)
        search_query = ('<record type="%s" database="@aproachDatabase@"><select><field sword="S0C09"/>'
                        '<field sword="S0BEE"/></select><where><clause>'
                        '((TITL/%s) ((STAC/AA)|(STAC/AC)) (DADT/%s - DADT/%s)</clause></where></record>' % (
                            str(recType).upper(), title, startDate,
                            endDate))
        xml_string = self._wpclient.service.search(search_query)
        dom = minidom.parseString(xml_string)
        xml_record = dom.getElementsByTagName('record')
        return [r.attributes['id'].value for r in xml_record]
