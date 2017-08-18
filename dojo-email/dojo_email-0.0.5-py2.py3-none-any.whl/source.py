from __future__ import absolute_import, print_function, unicode_literals

import os
import io
import logging
import imaplib
import uuid

from email.utils import parsedate_tz, mktime_tz, unquote
from email.parser import Parser
from datetime import datetime, date, timedelta

from dojo.vanilla.dataset import VanillaDataset


class MessageParser(Parser):

    def parsestr(self, text, headersonly=False):
        return self.parse(io.StringIO(text), headersonly=headersonly)


def message_from_string(s, *args, **kws):
    return MessageParser(*args, **kws).parsestr(s)


def collapse_rfc2231_value(value, errors='replace', fallback_charset='us-ascii'):
    if isinstance(value, tuple):
        rawval = unquote(value[2])
        charset = value[0] or 'us-ascii'
        try:
            return rawval.encode(charset, errors)
        except LookupError:
            return rawval.encode(fallback_charset, errors)
    else:
        return unquote(value)


def get_filename(message, failobj=None):
    missing = object()
    filename = message.get_param('filename', missing, 'content-disposition')
    if filename is missing:
        filename = message.get_param('name', missing, 'content-type')
    if filename is missing:
        return failobj
    return collapse_rfc2231_value(filename).strip().decode('utf-8')


class EmailSource(VanillaDataset):
    '''
    Extract and build meta data about drops from messages in a given email inbox.

    https://tools.ietf.org/html/rfc2822
    '''

    CONFIG = {
        'type': 'object',
        'properties': {
            'days': {'type': 'integer', 'default': 1},
            'connection': {'type': 'object', 'properties': {
                'imap_host': {'type': 'string'},
                'imap_port': {'type': 'integer'},
                'email_user': {'type': 'string'}
            }}
        }
    }

    SECRETS = {
        'type': 'object',
        'properties': {
            'connection': {'type': 'object', 'properties': {
                'email_password': {'type': 'string'}
            }}
        }
    }

    OUTPUT = {
        'type': 'object',
        'properties': {
            'id': {'type': 'string'},
            'date': {'type': 'string', 'format': 'date-time'},
            'resent_date': {'type': 'string', 'format': 'date-time', 'required': False},
            'from': {'type': 'string'},
            'subject': {'type': 'string'},
            'to': {'type': 'string'},
            'cc': {'type': 'string', 'required': False},
            'resent_to': {'type': 'string', 'required': False},
            'resent_cc': {'type': 'string', 'required': False},
            'parts': {'type': 'array', 'items': {
                'properties': {
                    'part_filename': {'type': 'string', 'required': False},
                    'content_type': {'type': 'string'},
                    'content_bytes': {'type': 'string'}
                }
            }}
        }
    }

    def process(self, inputs):
        mail = imaplib.IMAP4_SSL(self.config['connection']['imap_host'], self.config['connection']['imap_port'])
        mail.login(self.config['connection']['email_user'], self.secrets['connection']['email_password'])
        mail.select('"INBOX"', readonly=True)

        days = self.config.get('days', 1)  # default to 1 day ago
        start_date = (date.today() - timedelta(days=days)).strftime('%d-%b-%Y')
        query = '%s SENTSINCE %s ALL' % (self.config['query'], start_date)
        print('Searching for emails matching: %s' % (query, ))
        result, data = mail.uid('SEARCH', None, query.decode('utf-8'))
        email_uids = data[0].split()
        email_uids = [uid.decode('utf-8') for uid in email_uids]
        if len(email_uids) == 0:
            print('No email results for %s' % (query, ))
            return []
        result, data = mail.uid('FETCH', ','.join(email_uids), '(RFC822)')
        rows = []
        for datum in data:
            if len(datum) != 2:
                logging.info('imap fetch returned invalid entry: %s' % (datum, ))
                continue
            email_id = datum[0].decode('utf-8')
            try:
                body = datum[1].decode('utf-8')
            except UnicodeDecodeError as e:
                logging.info('failed to decode email body as utf-8, trying latin-1', e)
                body = datum[1].decode('latin-1')
            message = message_from_string(body)
            row = self._build_email_row(email_id, message)
            rows.append(row)
        return rows

    def _build_email_row(self, email_id, message):
        return {
            'id': email_id,
            'date': self._parse_rfc2822_datetime(message['Date']),
            'resent_date': self._parse_rfc2822_datetime(message['Resent Date']) if message['Resent Date'] else None,
            'from': message['From'],
            'subject': message['Subject'],
            'to': message['To'],
            'cc': message['CC'],
            'resent_to': message['Resent-To'],
            'resent_cc': message['Resent-CC'],
            'parts': self._build_part_rows(email_id, message)
        }

    def _parse_rfc2822_datetime(self, s):
        return datetime.fromtimestamp(mktime_tz(parsedate_tz(s)))

    def _build_part_rows(self, email_id, message):
        rows = []
        if message.is_multipart():
            for part in message.get_payload():
                rows += self._build_part_rows(email_id, part)
        else:
            rows.append(self._build_part_row(email_id, message))
        return rows

    def _build_part_row(self, email_id, message):
        # file_path = self._write_file(email_id, message)
        return {
            'part_filename': get_filename(message),
            'content_type': message.get_content_type(),
            'content_bytes': message.get_payload(decode=True)
        }

    def _write_file(self, email_id, message):
        part_filename = message.get_filename()
        file = io.BytesIO(message.get_payload(decode=True))
        unique_filename = str(uuid.uuid4())[:8]
        if part_filename and '.' in part_filename:
            unique_filename += '.%s' % (part_filename.split('.')[-1].lower(), )
        file_path = os.path.join(email_id, unique_filename)
        return self.store.write_file(file_path, file)
