import os
import logging
log = logging.getLogger('prospecting.env')

PROJECTNAME = os.getenv('P_PROJECTNAME', default='prospecting')

prjct_path = os.path.expanduser(os.path.join('~', ('.' + PROJECTNAME)))
PROJECTDIR = os.getenv('P_PROJECTDIR', default=prjct_path)
CREDSDIR = os.getenv('P_CREDSDIR', default=os.path.join(PROJECTDIR, 'credentials'))
CERTSDIR = os.getenv('P_CERTSDIR', default=os.path.join(CREDSDIR, 'certs'))
DATADIR = os.getenv('P_DATADIR', default=os.path.join(PROJECTDIR, 'data'))
TMPDIR = os.getenv('P_TMPDIR', default=os.path.join(DATADIR, 'tmp'))

LOG_FILENAME = 'prospecting.log'
LOG_FILENAME_DEBUG = 'debug.log'
LOG_FILE = os.path.join(TMPDIR, LOG_FILENAME)
LOG_FILE_DEBUG = os.path.join(TMPDIR, LOG_FILENAME_DEBUG)

CLIENT_SECRET_FILE = 'client_secret.json'
SOURCE_FILE = 'data.csv'
SOURCE_CSV = os.path.join(DATADIR, SOURCE_FILE)

NOAUTH_LOCAL_WEBSERVER = True

if not os.path.exists(CERTSDIR):
    os.makedirs(CERTSDIR)
    log.info('Created CERTSDIR directory at {0}\n\n'
             'Save your client_secrets.json file in the'
             'credentials directory prior to authenticating'
             'any of the GoogleApi classes.\n {1}'.format(CERTSDIR, '-' * 10))
if not os.path.exists(TMPDIR):
    os.makedirs(TMPDIR)
    log.info('Created TMPDIR directory at {0}\n\n'
             'Check the tmp directory for log files.\n {1}'.format(TMPDIR, '-' * 10))
