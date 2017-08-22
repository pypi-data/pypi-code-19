from datetime import datetime
import email.charset
import email.header
import email.mime.multipart
import email.mime.text
import email.utils

from .utils import to_unicode
from .constants import DEFAULT_STR_ENCODING
from .constants import DEFAULT_STR_ENCODING_ERRORS
from .address import parse_addresses


# Email using utf-7 should use Quoted Printables for non-ascii chars.  This
# way the message will be at least partially human-readable
email.charset.add_charset('utf-7', email.charset.QP, email.charset.QP)


def parse_date(d):
    if isinstance(d, datetime):
        # already a date?
        return d
    elif isinstance(d, basestring):
        timetuple = email.utils.parsedate_tz(d)
        unixtime = email.utils.mktime_tz(timetuple)
        return datetime.utcfromtimestamp(unixtime)
    else:
        return datetime.utcfromtimestamp(int(d))


def encode_header(value, encoding='utf7'):
    value = unicode(value)
    try:
        return email.header.Header(value.encode('ascii'))
    except UnicodeError:
        return email.header.Header(value.encode(encoding), encoding)


def encode_address_header(addresses):
    ret = email.header.Header()

    for idx, address in enumerate(addresses):
        if idx != 0:
            ret.append(', ')
        try:
            ret.append(address.encode('ascii'))
        except UnicodeError:
            # non-ascii?
            name, address = email.utils.parseaddr(address)
            ret.append(name.encode('utf-7'), 'utf-7')
            ret.append(' <%s>' % address)

    return ret


def construct_body(
        text,
        html,
        encoding=DEFAULT_STR_ENCODING,
        encoding_errors=DEFAULT_STR_ENCODING_ERRORS):

    def text_part(content, subtype):
        content = to_unicode(content, encoding, encoding_errors)
        MT = email.mime.text.MIMEText
        try:
            return MT(content.encode('ascii'), subtype, 'ascii')
        except UnicodeError:
            return MT(content.encode('utf-7'), subtype, 'utf-7')

    tp = text_part(text, 'plain') if text else None
    hp = text_part(html, 'html') if html else None

    if tp and hp:
        # both parts are non-empty
        message = email.mime.multipart.MIMEMultipart('alternative', None, [tp, hp])
    else:
        # at most one part is non-empty
        message = tp or hp or text_part('', 'plain')

    return message


def set_headers(
        msg,
        subject,
        to=[],
        cc=[],
        bcc=[],
        fromaddr=[],
        date=None):

    if subject:
        msg['Subject'] = encode_header(subject)

    msg['Date'] = encode_header(email.utils.formatdate(int(date.strftime('%s'))))

    if to:
        msg['To'] = encode_address_header(to)
    if cc:
        msg['CC'] = encode_address_header(cc)
    if bcc:
        msg['BCC'] = encode_address_header(bcc)
    if fromaddr:
        msg['From'] = encode_address_header(fromaddr)


def construct(
        subject='',
        text='',
        html='',
        to=[],
        cc=[],
        bcc=[],
        fromaddr=[],
        date=None,
        encoding=DEFAULT_STR_ENCODING,
        encoding_errors='ignore'):

    # prepare body
    msg = construct_body(
        text=text,
        html=html,
        encoding=encoding,
        encoding_errors=encoding_errors)

    # parse parameters
    to = parse_addresses(to, encoding, encoding_errors)
    cc = parse_addresses(cc, encoding, encoding_errors)
    bcc = parse_addresses(bcc, encoding, encoding_errors)
    fromaddr = parse_addresses(fromaddr, encoding, encoding_errors)
    date = parse_date(date or datetime.utcnow())

    # set headers
    set_headers(
        msg,
        subject=subject,
        to=to,
        cc=cc,
        bcc=bcc,
        fromaddr=fromaddr,
        date=date)

    recipients = [email.utils.parseaddr(addr)[1] for addr in to + cc + bcc]
    fromline = ', '.join(email.utils.parseaddr(addr)[1] for addr in fromaddr)

    return msg, fromline, recipients
