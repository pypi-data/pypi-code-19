__author__ = 'pvde'

"""
Module that provides functionality to determine if a CPA "matches" a CPP.  This is the
case if it can be established that the Party in the CPP matches either the Party or the
CounterParty in the CPA and that the service specifications match accordingly.

"""

import logging, traceback, re, lxml, isodate

from schema import cppa3_content_model

_NSMAP = {'cppa': 'http://docs.oasis-open.org/ebcore/ns/cppa/v3.0',
         'ds': 'http://www.w3.org/2000/09/xmldsig#',
         'xml': 'http://www.w3.org/XML/1998/namespace',
         'xkms': 'http://www.w3.org/2002/03/xkms#',
         'dsig11' : 'http://www.w3.org/2009/xmldsig11#'
         }

class MatchException(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

def match(cpp, cpa, handle_defaults=False):
    """
    @param cpp:
    @param cpa:
    @return: a Boolean indication of the success of the match
    """
    party_name, direction, this_role_element, other_role_element = match_parties(cpp, cpa)
    match_service_specifications(cpp, cpa, direction, this_role_element, other_role_element)
    return party_name

def match_parties(cpp, cpa):
    try:
        party_name = match_partyinfo(cpp.xpath('cppa:PartyInfo',
                                               namespaces=_NSMAP)[0],
                                     cpa.xpath('cppa:PartyInfo',
                                               namespaces=_NSMAP)[0])
        direction = lambda x: x
        this_role_element, other_role_element, id_position = 'cppa:PartyRole', 'cppa:CounterPartyRole', 0
    except:
        party_name = match_partyinfo(cpp.xpath('cppa:PartyInfo',
                                               namespaces=_NSMAP)[0],
                                     cpa.xpath('cppa:CounterPartyInfo',
                                               namespaces=_NSMAP)[0])
        direction = reverse
        this_role_element, other_role_element, id_position = 'cppa:CounterPartyRole', 'cppa:PartyRole', 1
    match_profileinfo(cpp, cpa, id_position)
    return party_name, direction, this_role_element, other_role_element

def match_partyinfo(cpp_partyinfo, cpa_partyinfo):
    cpa_party_name = cpa_partyinfo.xpath(
        'cppa:PartyName/text()', namespaces=_NSMAP
    )[0]
    cpp_party_name = cpp_partyinfo.xpath(
        'cppa:PartyName/text()', namespaces=_NSMAP
    )[0]
    if cpa_party_name != cpp_party_name:
        raise MatchException('Mismatch in party name: {} versus {}'.format(cpp_party_name,
                                                                           cpa_party_name))
    # All PartyIDs in the CPA PartyInfo must be present in the CPP PartyInfo
    #for party_id in cpp_partyinfo.xpath('cppa:PartyID')
    for party_id in cpa_partyinfo.xpath(
        'cppa:PartyID', namespaces=_NSMAP
    ):
        party_id_value = party_id.text
        if party_id.get('type') == None:
            cpp_partyid_list = cpp_partyinfo.xpath('cppa:PartyID/text()="{}"'.format(party_id_value),
                                                   namespaces=_NSMAP)
        else:
            cpp_partyid_list = cpp_partyinfo.xpath('cppa:PartyID[@type="{}"]/text()="{}"'.format(party_id.get('type'),
                                                                                                 party_id_value))
        if not cpp_partyid_list:
            raise MatchException('Party ID {} not found in CPA'.format(party_id_value))


    return cpp_party_name

def match_profileinfo(cpp, cpa, id_position):
    cpp_profile_identifier_element = cpp.xpath('cppa:ProfileInfo/cppa:ProfileIdentifier',
                                               namespaces=_NSMAP)[0]
    profile_identifier_elements = cpa.xpath('cppa:AgreementInfo/cppa:ProfileIdentifier',
                                    namespaces=_NSMAP)
    if len(profile_identifier_elements) == 2:
        assert_equal(cpp_profile_identifier_element.text,
                     profile_identifier_elements[id_position].text)

    cpp_expirations = cpp.xpath('cppa:ProfileInfo/cppa:ExpirationDate',
                                   namespaces=_NSMAP)
    cpa_expirations = cpp.xpath('cppa:ProfileInfo/cppa:ExpirationDate',
                                   namespaces=_NSMAP)

    if cpp_expirations and cpa_expirations:
        cpp_exp_date = isodate.parse_datetime(cpp_expirations[0].text)
        cpa_exp_date = isodate.parse_datetime(cpa_expirations[0].text)
        if cpa_exp_date > cpp_exp_date:
            raise MatchException('Expiration {} must precede {}'.format(cpp_expirations[0].text,
                                                                        cpa_expirations[0].text))
    cpp_activations = cpp.xpath('cppa:ProfileInfo/cppa:ActivationDate',
                                   namespaces=_NSMAP)
    cpa_activations = cpp.xpath('cppa:ProfileInfo/cppa:ActivationDate',
                                   namespaces=_NSMAP)
    if cpp_activations and cpa_activations:
        cpp_act_date = isodate.parse_datetime(cpp_activations[0].text)
        cpa_act_date = isodate.parse_datetime(cpa_activations[0].text)
        if cpa_act_date < cpp_act_date:
            raise MatchException('Activation {} must precede {}'.format(cpp_activations[0].text,
                                                                        cpa_activations[0].text))



def match_service_specifications(cpp, cpa, direction, this_role_element, other_role_element):
    for cpa_service_specification in cpa.xpath('cppa:ServiceSpecification', namespaces=_NSMAP):
        party_role = cpa_service_specification.xpath('{}/@name'.format(this_role_element), namespaces=_NSMAP)[0]
        counterparty_role= cpa_service_specification.xpath('{}/@name'.format(other_role_element), namespaces=_NSMAP)[0]
        logging.info('CPA {} in CPP {}, CPA {} in CPP {}'.format(party_role,
                                                                 this_role_element,
                                                                 counterparty_role,
                                                                 other_role_element))
        cpp_service_specification = cpp.xpath(
            'cppa:ServiceSpecification[cppa:PartyRole/@name="{}" and cppa:CounterPartyRole/@name="{}"]'.format(party_role,
                                                                                                               counterparty_role),
            namespaces=_NSMAP
        )[0]
        for cpa_service_binding in cpa_service_specification.xpath(
            'cppa:ServiceBinding', namespaces=_NSMAP
        ):
            match_cpa_service_binding(cpp, cpp_service_specification, cpa, cpa_service_binding,
                                      party_role, counterparty_role, direction)

def match_cpa_service_binding(cpp, cpp_service_specification, cpa, cpa_service_binding,
                              party_role, counterparty_role, direction):
    cpa_service_element = cpa_service_binding.xpath('cppa:Service', namespaces=_NSMAP)[0]
    cpa_service = cpa_service_element.text
    cpa_service_type = cpa_service_element.get('type')
    logging.info('Matching service binding for {}, {}, roles {}, {}'.format(cpa_service, cpa_service_type,
                                                                            party_role, counterparty_role))
    cpp_service_binding = cpp_service_specification.xpath(service_xpath(cpa_service, cpa_service_type),
                                                          namespaces=_NSMAP)[0]
    match_service_bindings(cpp, cpp_service_binding, cpa, cpa_service_binding, cpa_service, direction)


def service_xpath(value, type):
    if type != None:
        return 'cppa:ServiceBinding[cppa:Service[@type="{}"]/text()="{}"]'.format(type, value)
    else:
        return 'cppa:ServiceBinding[cppa:Service/text()="{}"]'.format(value)

def match_service_bindings(cpp, cpp_service_binding, cpa, cpa_service_binding, cpa_service, direction):
    for cpa_action_binding in cpa_service_binding.xpath(
        'cppa:ActionBinding', namespaces=_NSMAP
    ):
        cpa_action = cpa_action_binding.get('action')
        cpa_direction = cpa_action_binding.get('sendOrReceive')
        logging.info('For {}, checking CPA action {} ({})'.format(cpa_service, cpa_action, cpa_direction))
        cpp_action_binding = cpp_service_binding.xpath(
            'cppa:ActionBinding[@action="{}" and @sendOrReceive="{}"]'.format(cpa_action, direction(cpa_direction)),
            namespaces=_NSMAP
        )[0]
        match_action_bindings(cpp, cpp_action_binding, cpa, cpa_action_binding)
    # @todo also do the check that all actions that the CPP considers required are present in the CPA

def match_action_bindings(cpp, cpp_action_binding, cpa, cpa_action_binding):
    cpa_channel_id_element = cpa_action_binding.xpath('cppa:ChannelId', namespaces=_NSMAP)[0]
    for cpp_channel_id_element in cpp_action_binding.xpath('cppa:ChannelId', namespaces=_NSMAP):
        cpa_channel_id = cpa_channel_id_element.text
        cpp_channel_id = cpp_channel_id_element.text
        try:
            match_channels(cpp, cpp_channel_id, cpa, cpa_channel_id)
            logging.info('Matched CPA channel {} to CPP channel {}'.format(cpa_channel_id,
                                                                           cpp_channel_id))
            return cpp_channel_id
        except:
            exception = str(traceback.format_exc())
            logging.info('Unable to match CPA channel {} to CPP channel {}: {}'.format(cpa_channel_id,
                                                                                       cpp_channel_id,
                                                                                       exception))
    # if we're here, all matches raised exceptions
    exception = 'Unable to match CPA channel {} to any CPP channel'.format(cpa_channel_id)
    logging.info(exception)
    raise MatchException(exception)

def match_channels(cpp, cpp_channel_id, cpa, cpa_channel_id):
    logging.info('Checking CPA channel {} and CPP channel {}'.format(cpa_channel_id,
                                                                     cpp_channel_id))
    cpp_channel = cpp.xpath('*[@id="{}"]'.format(cpp_channel_id))[0]
    cpa_channel = cpa.xpath('*[@id="{}"]'.format(cpa_channel_id))[0]
    assert_equal(cpp_channel.tag, cpa_channel.tag)
    match_schema(cpp, cpp_channel, cpa, cpa_channel)
    match_transports(cpp, cpp_channel, cpa, cpa_channel)

def match_transports(cpp, cpp_channel, cpa, cpa_channel):
    cpp_transport_id = cpp_channel.get('transport')
    cpa_transport_id = cpa_channel.get('transport')
    if cpp_transport_id != None and cpa_transport_id != None:
        cpp_transport = cpp.xpath('*[@id="{}"]'.format(cpp_transport_id))[0]
        cpa_transport = cpa.xpath('*[@id="{}"]'.format(cpa_transport_id))[0]
        match_schema(cpp, cpp_transport, cpa, cpa_transport)


def match_schema(cpp, cpp_element, cpa, cpa_element):
    if cpa_element.tag in cppa3_content_model:
        # the element is a complex element
        if cpa_element.tag in _allowed_non_matching_complex_elements:
            logging.info('Skipping exceptional {}'.format(cpa_element.tag))
        else:
            logging.info('Checking complex element {}'.format(cpa_element.tag))
            for cpa_child_element in cpa_element:
                if cpa_child_element.tag in cppa3_content_model:
                    if cpa_child_element.tag in _allowed_non_matching_complex_elements:
                        logging.info('Skipping exceptional {}'.format(cpa_child_element.tag))
                    else:
                        logging.info('Checking complex child element {}'.format(cpa_child_element.tag))
                        cpp_child_element = retrieve_child_element(cpa_child_element.tag, cpp_element)
                        match_schema(cpp, cpp_child_element, cpa, cpa_child_element)
                        logging.info('Checked complex child element {}'.format(cpa_child_element.tag))
                else:
                    if cpa_child_element.tag in _allowed_non_matching_simple_elements:
                        logging.info('Skipping exceptional {}'.format(cpa_child_element.tag))
                    elif cpa_child_element.tag in _channel_referencing_elements:
                        logging.info('Processing channel reference {}'.format(cpa_child_element.tag))
                        match_channel_reference_element(cpp, cpp_element, cpa, cpa_child_element)
                    elif cpa_child_element.tag in _certificate_referencing_elements:
                        match_certificate_reference_element(cpp, cpp_element, cpa, cpa_child_element)
                    else:
                        logging.error('Simple element:  {}'.format(cpa_child_element.tag))
                        match_simple_child_element(cpp_element, cpa_child_element)


def assert_equal(value_1, value_2):
    if value_1 != value_2:
        raise MatchException('{} != {}'.format(value_1, value_2))

def retrieve_child_element(child_element_tag, parent_element):
    local_name = re.split('\}', child_element_tag)[1]
    child_element_list = parent_element.xpath(
        'cppa:'+local_name, namespaces=_NSMAP)
    if len(child_element_list) == 0:
        message = 'At least 1 {} required in {}'.format(child_element_tag,
                                                        parent_element.tag)
        logging.info(message)
        raise MatchException(message)
    else:
        logging.info('Found one {}'.format(child_element_tag))
        return child_element_list[0]

def match_simple_child_element(parent_element, child_element):
    local_name = re.split('\}', child_element.tag)[1]
    corresponding_elements = parent_element.xpath(
        'cppa:{}'.format(local_name),
        namespaces=_NSMAP
    )
    if len(corresponding_elements) > 0:
        candidate_matches = parent_element.xpath(
            'cppa:{}[text()="{}"]'.format(local_name, child_element.text),
            namespaces=_NSMAP
        )
        if len(candidate_matches) == 0:
            message = 'No child element {} found with content {} in {}'.format(child_element.tag,
                                                                               child_element.text,
                                                                               parent_element.tag)
            logging.info(message)
            raise MatchException(message)
    else:
        logging.info('Found one {}'.format(child_element.tag))

def match_channel_reference_element(cpp, parent_element, cpa, child_element):
    local_name = re.split('\}', child_element.tag)[1]
    candidate_matches = parent_element.xpath(
        'cppa:{}'.format(local_name),
        namespaces=_NSMAP
    )
    if len(candidate_matches) == 0:
        message = 'No child element {} found in {}'.format(child_element.tag,
                                                           parent_element.tag)
        logging.info(message)
        raise MatchException(message)
    else:
        cpp_channel_id = candidate_matches[0].text
        logging.info('Matching referenced {} channels {} and {}'.format(child_element.tag,
                                                                        child_element.text,
                                                                        cpp_channel_id))
        match_channels(cpp, cpp_channel_id, cpa, child_element.text)

def match_certificate_reference_element(cpp, parent_element, cpa, child_element):
    local_name = re.split('\}', child_element.tag)[1]
    logging.error('match_certificate_reference_element for {}'.format(local_name))
    candidate_matches = parent_element.xpath(
        'cppa:{}'.format(local_name),
        namespaces=_NSMAP
    )
    cpa_certificate_id = child_element.get('certId')
    cpa_certificate = cpa.xpath('descendant::cppa:Certificate[@id="{}"]'.format(cpa_certificate_id),
                                namespaces=_NSMAP)[0]
    if len(candidate_matches) == 0:
        message = 'IN CPP, no child element {} found in {} id {}'.format(child_element.tag,
                                                                         parent_element.tag,
                                                                         cpa_certificate_id)
        logging.info(message)
        check_cpa_cert_with_cpp_trust_anchors(cpp, parent_element, cpa_certificate, local_name)
    else:
        cpp_certificate_id = candidate_matches[0].get('certId')
        logging.info('Matching referenced {} certificates {} and {}'.format(child_element.tag,
                                                                            cpa_certificate_id,
                                                                            cpp_certificate_id))
        cpp_certificate = cpp.xpath('descendant::cppa:Certificate[@id="{}"]'.format(cpp_certificate_id),
                                    namespaces=_NSMAP)[0]
        match_certificates(cpa_certificate, cpp_certificate)

def match_certificates(cpa_certificate, cpp_certificate):
    cpa_keyname = cpa_certificate.xpath('ds:KeyInfo/ds:KeyName/text()',
                                        namespaces=_NSMAP)
    cpp_keyname = cpp_certificate.xpath('ds:KeyInfo/ds:KeyName/text()',
                                        namespaces=_NSMAP)
    assert_equal(cpa_keyname, cpp_keyname)
    cpa_leaf_x509_cert = cpa_certificate.xpath('ds:KeyInfo/ds:X509Data[0]/ds:X509Certificate[0]/text()',
                                        namespaces=_NSMAP)
    cpp_leaf_x509_cert = cpp_certificate.xpath('ds:KeyInfo/ds:X509Data[0]/ds:X509Certificate[0]/text()',
                                        namespaces=_NSMAP)
    assert_equal(cpa_leaf_x509_cert, cpp_leaf_x509_cert)

def check_cpa_cert_with_cpp_trust_anchors(cpp, cpp_parent, cpa_certificate, local_name):
    cpa_x509_certificate_chain = cpa_certificate.xpath('descendant-or-self::ds:X509Certificate',
                                                       namespaces=_NSMAP)

    if len(cpa_x509_certificate_chain) > 0:
        cpa_x509_certificate_root = remove_all_whitespace(
            cpa_x509_certificate_chain[-1].text
        )
        logging.debug('Root cert is {} ... {} (len: {})'.format(cpa_x509_certificate_root[0:6],
                                                                cpa_x509_certificate_root[-6:],
                                                                len(cpa_x509_certificate_root)))
        cert_type = re.split('^(.+)CertificateRef$', local_name)[1]
        trust_anchor_refs = cpp_parent.xpath('cppa:{}TrustAnchorSetRef'.format(cert_type),
                                            namespaces=_NSMAP)

        if len(trust_anchor_refs) > 0:
            trust_anchor_set_id = trust_anchor_refs[0].get('certId')
            trust_anchor_set = cpp.xpath('descendant::cppa:*[@id="{}"]'.format(trust_anchor_set_id),
                                         namespaces=_NSMAP)[0]
            rootfound = False
            for anchor_certificate_ref in trust_anchor_set.xpath('cppa:AnchorCertificateRef',
                namespaces=_NSMAP):
                anchor_certificate_ref_id = anchor_certificate_ref.get('certId')
                logging.info('CCC {}'.format(anchor_certificate_ref_id))
                trusted_ca_certificate = cpp.xpath(
                    'descendant::cppa:Certificate[@id="{}"]'.format(anchor_certificate_ref_id),
                    namespaces=_NSMAP
                )[0]
                trusted_ca_certificate_x509 = remove_all_whitespace(
                    trusted_ca_certificate.xpath(
                        'descendant::ds:X509Certificate', namespaces=_NSMAP
                    )[-1].text
                )
                if trusted_ca_certificate_x509 == cpa_x509_certificate_root:
                    rootfound = True
            if not rootfound:
                for trusted_ca_certificate in trust_anchor_set.xpath(
                        'cppa:Certificate', namespaces=_NSMAP
                ):
                    trusted_ca_certificate_x509 = remove_all_whitespace(
                        trusted_ca_certificate.xpath(
                            'descendant::ds:X509Certificate', namespaces=_NSMAP
                        )[-1]
                    )
                    if trusted_ca_certificate_x509 == cpa_x509_certificate_root:
                        rootfound = True
            if not rootfound:
                raise MatchException('Did not find a matching trusted root certificate')


def reverse(direction):
    if direction == 'send':
        return 'receive'
    else:
        return 'send'

def cppa(el):
    return '{{{}}}{}'.format(_NSMAP['cppa'], el)

_allowed_non_matching_complex_elements = [
    cppa('RetryHandling')
]

_allowed_non_matching_simple_elements = [
    cppa('Description'),
    cppa('Username'),
    cppa('Password')
]

_channel_referencing_elements = [
    cppa('ReceiverErrorsReportChannelId'),
    cppa('ReceiptChannelId'),
    cppa('PullChannelId')
]

_certificate_referencing_elements = [
    cppa('SigningCertificateRef'),
    cppa('EncryptionCertificateRef'),
    cppa('ClientCertificateRef'),
    cppa('ServerCertificateRef')
]

def check_x509_data_content(anchorid, rootcert, anchor_certid, cpp):
    anchor_cert = cpp.xpath(
        'descendant::cppa:Certificate[@id="{}"]'.format(anchor_certid),
        namespaces=_NSMAP)[0]
    return check_x509_data_content_2(anchorid, rootcert, anchor_certid, anchor_cert)

def check_x509_data_content_2(rootcert, anchor_certid, anchor_cert):
    anchor_cert_data = anchor_cert.xpath(
        'descendant::ds:X509Certificate/text()',
        namespaces=_NSMAP)[0]
    anchor_cert_data = remove_all_whitespace(anchor_cert_data)
    logging.debug(
        'Comparing against {} {} ... {} (len: {})'.format(anchor_cert_data[0:6],
                                                          anchor_cert_data[-6:],
                                                          len(anchor_cert_data)))
    if str(rootcert) == str(anchor_cert_data):
        logging.info(
            'Referenced X509Certificate found in anchor {} cert {}'.format(anchorid,
                                                                           anchor_certid))
        return True
    else:
        return False

def remove_all_whitespace(inputstring):
    pattern = re.compile(r'\s+')
    return re.sub(pattern, '', inputstring)

