import os
import os.path
import httplib2
import datetime

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly',
          'https://www.googleapis.com/auth/drive']
CLIENT_SECRET_FILE = '/home/jedaube/meet/interface/meet_client_secret.json'
APPLICATION_NAME = 'Meeting Pro'


class GoogleAPI:

    def __init__(self):
        '''Instantiates a google api'''

        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
        Credentials, the obtained credential.
        """
        home_dir = os.path.expanduser('~')
        credential_dir = os.path.join(home_dir, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       'meet_client_secret.json')

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
            flow.user_agent = APPLICATION_NAME
            flags = tools.argparser.parse_args(args=[])
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)

        http = credentials.authorize(httplib2.Http())
        self.serviceCal = discovery.build('calendar', 'v3', http=http)
        self.serviceDrive = discovery.build('drive', 'v3', http=http)

    def get_meeting(self):
        '''Gets a meeting object from user calendar'''
        #  'Z' indicates UTC time
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        s = self.serviceCal
        meetingsResult = s.events().list(
            calendarId='primary',
            timeMin=now,
            maxResults=1,
            singleEvents=True,
            orderBy='startTime').execute()
        meetings = meetingsResult.get('items', [])
        return meetings

    def create_google_doc(self, file_path, file_name):
        '''Write one to many meeting files to google drive'''
        file_metadata = {
            'name': file_name,
            'mimeType': 'application/vnd.google-apps.document'
        }
        media = MediaFileUpload(file_path,
                                mimetype='text/HTML')
        s = self.serviceDrive
        file = s.files().create(body=file_metadata,
                                media_body=media,
                                fields='id').execute()
        response = file.get('id')
        return response
