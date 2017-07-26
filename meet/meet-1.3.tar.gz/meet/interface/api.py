import os
import os.path
import httplib2
import datetime

from googleapiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload

APPLICATION_NAME = 'Meeting Pro'
HOME_DIR = os.path.expanduser('~')


class GoogleAPI:

    def __init__(self, app_conf):
        '''Instantiates a google api'''

        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
        Credentials, the obtained credential.
        """
        scopes = ['https://www.googleapis.com/auth/calendar.readonly',
                  'https://www.googleapis.com/auth/drive']
        client_secret_file_name = app_conf.configs['client_secret_file_name']
        client_secret_file_path = os.path.join(
            app_conf.configs['client_secret_file_location'],
            client_secret_file_name
        )
        credential_dir = os.path.join(HOME_DIR, '.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir,
                                       client_secret_file_name)

        store = Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(client_secret_file_path,
                                                  scopes)
            flow.user_agent = APPLICATION_NAME
            flags = tools.argparser.parse_args(args=[])
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else:  # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
            print('Storing credentials to ' + credential_path)
            print('Execute the command again to generate meeting notes')

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
