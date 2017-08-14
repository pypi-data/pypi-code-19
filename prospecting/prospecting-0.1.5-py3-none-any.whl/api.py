
import os
import json
import time

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import pandas as pd

from prospecting.env import (PROJECTNAME,
                             CREDSDIR,
                             CLIENT_SECRET_FILE,
                             DATADIR,
                             NOAUTH_LOCAL_WEBSERVER
                             )

try:
    import argparse
    parser = argparse.ArgumentParser(parents=[tools.argparser])
    parser.set_defaults(noauth_local_webserver=NOAUTH_LOCAL_WEBSERVER)
    flags = parser.parse_known_args()[0]
except ImportError:
    flags = None

from prospecting.errors import BadInputError

import logging
log = logging.getLogger('prospecting.api')
log.info('flags are:\n{0}'.format(flags))


class GoogleApi:
    """Base class for interfacing with Google APIs


    https://developers.google.com/apis-explorer/

    """

    def __init__(self, apiname, apiversion, scopelist, discoveryurl=None):
        """Initialize GoogleApi base class

        :param str apiname:  Name of Google API, example: 'sheets'
        :param str apiversion: Version of API, example: 'v4'
        :param list scopelist:   List of authorization scopes, example: []

        """
        self.api_name = apiname
        self.api_version = apiversion
        self.api_id = (self.api_name + ":" + self.api_version)
        self.api_scope = scopelist

        if discoveryurl is None:
            self.discovery_url = ('https://www.googleapis.com/discovery/v1/apis/' + self.api_name +
                                  '/' + self.api_version + '/rest')
        else:
            self.discovery_url = discoveryurl

        self.api_info = self._discover_api(self.discovery_url)
        self.info = {}  # for storing metadata and misc values

    def authenticate(self):
        log.info('Authenticating...{0}, {1}'.format(self.api_name, self.api_version))
        self.credentials = self._get_credentials(self.api_scope)
        self.http = self.credentials.authorize(httplib2.Http())
        service = self._build_service_object()
        log.info('Successfully authenticated...{0}, {1}'.format(self.api_name, self.api_version))
        return service

    def reauthenticate(self, scopelist):
        if os.path.isfile(self.credential_path):
            os.remove(self.credential_path)
        self.api_scope = scopelist
        self.authenticate()

    def _get_credentials(self, scopelist):
        log.info('Getting credentials...')
        credsfile = ('googleapis.' + self.api_name + '.' + PROJECTNAME + '.json')
        self.credential_path = os.path.join(CREDSDIR, credsfile)
        self.store = Storage(self.credential_path)
        file_exists = os.path.isfile(self.credential_path)
        scopes_match = False
        if file_exists:
            with open(self.credential_path) as f:
                credjson = json.load(f)
            scopes_match = set(credjson['scopes']) == set(scopelist)
        if scopes_match:
            creds = self.store.get()
        else:
            creds = None
            if (not creds or creds.invalid):
                creds = self._run_credentials_flow()
        return creds

    def _run_credentials_flow(self):
        log.info('Running credentials flow...')
        secretspath = os.path.join(CREDSDIR, CLIENT_SECRET_FILE)
        flow = client.flow_from_clientsecrets(secretspath, self.api_scope)
        flow.user_agent = PROJECTNAME
        if flags or flags is None:
            self.credentials = tools.run_flow(flow, self.store, flags)
        else:  # Needed only for compatibility with Python 2.6
            self.credentials = tools.run(self.flow, self.store)
        log.info('Storing credentials to {0}'.format(self.credential_path))
        return self.credentials

    def _build_service_object(self):
        log.info('Building service object...')
        service_object = discovery.build(self.api_name,
                                         self.api_version,
                                         http=self.http,
                                         discoveryServiceUrl=self.discovery_url)
        log.info('Service object built...{0}'.format(service_object))
        return service_object

    def _discover_api(self, discoveryurl):
        discovery_file = os.path.join(DATADIR,
                                      'discoveryapi_' + self.api_name + '.json')
        if os.path.isfile(discovery_file):
            log.info(('Reading discovery file for {0}').format(self.api_id))
            with open(discovery_file) as f:
                disco_info = json.load(f)
        else:
            h = httplib2.Http()
            resp, content = h.request(discoveryurl, 'GET')
            log.info(('Resp from 1st discoveryurl attempt: {0}'.format(resp['status'])))
            if resp['status'] == '404':
                DISCOVERY_URI = 'https://www.googleapis.com/discovery/v1/apis?preferred=true'
                resp2, content2 = h.request(DISCOVERY_URI, 'GET')
                disco_all = json.loads(content2.decode())
                disco_api = [apiinfo for apiinfo in disco_all['items']
                             for k, v in apiinfo.items() if v == self.api_id][0]
                self.discovery_url = disco_api['discoveryRestUrl']
                resp, content = h.request(self.discovery_url, 'GET')
                if resp['status'] == '404':
                    try:
                        raise Exception(resp['status'])
                    except Exception as e:
                        log.error('Error response in 2nd discoveryurl attempt: {0}'.format(e))
                        assert resp['status'] != '404'
                else:
                    disco_info = json.loads(content.decode())
                    print(disco_info)
                    log.info(('Resp from 2nd discoveryurl attempt: {0}'.format(resp['status'])))
            disco_info = json.loads(content.decode())
            log.info(('Writing discovery file for {0}').format(self.api_id))
            with open(discovery_file, 'w') as outfile:
                json.dump(json.loads(content.decode()), outfile)
            log.info('Read from api, write to file complete. Check new file in' + discovery_file)
        return disco_info


class SheetsApi(GoogleApi):
    """Class for SheetsApi object


    https://developers.google.com/resources/api-libraries/documentation/sheets/v4/python/latest/
    https://developers.google.com/apis-explorer/#p/sheets/v4/

    """

    def __init__(self,
                 apiname='sheets',
                 apiversion='v4',
                 spreadsheetid=None,
                 sheetrange=None,
                 scopelist=['https://www.googleapis.com/auth/spreadsheets.readonly',
                            'https://www.googleapis.com/auth/drive.readonly']):
        self.spreadsheet_id = spreadsheetid
        self.sheet_range = sheetrange
        self.sheets = {}  # store data from get requests
        GoogleApi.__init__(self, apiname, apiversion, scopelist)

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)

    def get_ss_info(self, sheetranges=None, includegriddata=False):
        """Returns the spreadsheet from a given ID

        :param sheetranges: List of comma separated range names as strings
                            Ex: ['Sheet1','Sheet2!A1:B5]
        :param bool includegriddata: True if grid data should be returned, Ex: True
        :type sheetranges: list[str]
        :return:
            {
                "spreadsheetId": "1MdZzXvqftMJTfLdbBpzYJA42kCv9R6SSEAT5tSUNe5g",
                "properties": {
                    ...
                },
                "sheets": [
                    {
                        "properties": {
                            ...
                        },
                        ...
                    }
                ],
                "spreadsheetUrl": "https://docs.google.com/spreadsheets/d/.../edit"
            }
        :rtype: dict
        """
        spreadsheetid = self.spreadsheet_id
        if sheetranges is None:
            if spreadsheetid is None:
                raise ValueError('Please set self.spreadsheet_id')
            response = self.service.spreadsheets().get(
                spreadsheetId=spreadsheetid,
                includeGridData=includegriddata
            ).execute()
            log.info('Spreadsheet loaded.')
            log.info('Sheets include: {0}'.format([sheet['properties']['title']
                                                   for sheet in response['sheets']]))
            return response
        else:
            response = self.service.spreadsheets().get(
                spreadsheetId=spreadsheetid,
                ranges=sheetranges,
                includeGridData=includegriddata
            ).execute()
            return response

    def vet_input(self, dataframe):
        if isinstance(dataframe, type(pd.DataFrame())) is False:
            # raise error if object is not a Pandas dataframe
            log.error('Object must be of type {0}'.format(type(pd.DataFrame())))
            raise BadInputError
        else:
            return(dataframe)

    def get(self,
            sheetrange=None,
            asdataframe=True,
            headerrow=0,
            majordimension='ROWS',
            valuerenderoption='UNFORMATTED_VALUE',
            datetimerenderoption='SERIAL_NUMBER'):
        """Returns one range of values from a spreadsheet.

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/get

        :param str sheetrange: Name of range to get, Ex: ['Sheet1']
        :param bool asdataframe: Flag to determine response type, Ex: False
        :param int headerrow: Specifies location of header, Ex: 2
        :param str majordimension: The major dimension that results should use, Ex 'COLUMNS'
        :param str valuerenderoption: How values should be represented in the output
                                      Ex: 'FORMATTED_VALUE'
        :param str datetimerenderoption: How dates, times, and durations should be represented
                                         in the output
                                         Ex: 'FORMATTED_STRING'

        :returns: Google Sheet as requested
        :rtype: DataFrame

        """
        tmpdf = pd.DataFrame()
        spreadsheetid = self.spreadsheet_id
        if spreadsheetid is None:
            raise ValueError('Please set self.spreadsheet_id')
        if not sheetrange:
            sheetrange = self.sheet_range
        self.response = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheetid,
            range=sheetrange,
            majorDimension=majordimension,
            valueRenderOption=valuerenderoption,
            dateTimeRenderOption=datetimerenderoption
        ).execute()
        values = self.response.get('values', None)
        if not values:
            log.info('No data found.')
            tmpdf = None
        else:
            if headerrow is not 0:
                if asdataframe is True:
                    try:
                        tmpdf = pd.DataFrame.from_records(values[(headerrow + 1):len(values)],
                                                          columns=values[headerrow])
                    except AssertionError as err:
                        print('AssertionError: {0}'.format(err))
                        print('No columns in headerrow.'
                              'Add columns to sheet or pass headerrow=None.')
                        print('Check self.sheets for malformed response (no columns set).')
                else:
                    tmpdf = values[(headerrow + 1)]
            else:
                if asdataframe is True:
                    tmpdf = pd.DataFrame.from_records(values[1:len(values)], columns=values[0])
                else:
                    tmpdf = values[0:len(values)]
        return (tmpdf)

    def batchGet(self,
                 sheetranges,
                 majordimension='ROWS',
                 valuerenderoption='FORMATTED_VALUE',
                 datetimerenderoption='SERIAL_NUMBER'):
        """Returns one or more ranges of values from a spreadsheet.

        Params:
            sheetranges (list): List of comma separated range names as strings
                                Ex: ['Sheet1','Sheet2!A1:B5]
            majordimension (str): The major dimension that results should use, Ex 'COLUMNS'
            valuerenderoption (str): How values should be represented in the output
                                     Ex: 'UNFORMATTED_VALUE'
            datetimerenderoption (str): How dates, times, and durations should be represented
                                        in the output
                                        Ex: 'FORMATTED_STRING'

        Returns:
            List of tuples, one tuple for each range requested, Ex: [('col_1, col_2), ]


        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchGet

        """
        spreadsheetid = self.spreadsheet_id
        if spreadsheetid is None:
            raise ValueError('Please set self.spreadsheet_id')
        if not sheetranges:
            sheetranges = self.sheet_range
        self.response = self.service.spreadsheets().values().batchGet(
            spreadsheetId=spreadsheetid,
            ranges=sheetranges,
            majorDimension=majordimension,
            valueRenderOption=valuerenderoption,
            dateTimeRenderOption=datetimerenderoption
        ).execute()
        values = {vr['range']: vr.get('values', []) for vr in self.response['valueRanges']}
        if not values:
            print('No data found.')
        return {k: v for k, v in values.items()}

    def update(self, sheetrange, dataframe, **kwargs):
        """Sets values in a range of a spreadsheet

        Params:
            sheetrange (str):                   Name of range to update,
                                                Ex: 'Sheet1'

            dataframe (pd.DataFrame):           DataFrame object

            valueinputoption (str):             How the input data should be interpreted,
                                                Ex: 'USER_ENTERED'

            includevaluesinresponse (bool):     Determines if the update response should include
                                                the values of the cells that were updated,
                                                Ex. False

            responsevaluerenderoption (str):    Determines how values in the response
                                                should be rendered,
                                                Ex: 'UNFORMATTED_VALUE'

            responsedatetimerenderoption (str): Determines how dates, times, and durations
                                                in the response should be rendered,
                                                Ex: 'FORMATTED_STRING'

        Returns:
            response, returns "UpdateValuesResponse" in format:
                {
                  "spreadsheetId": string,
                  "updatedRange": string,
                  "updatedRows": number,
                  "updatedColumns": number,
                  "updatedCells": number,
                  "updatedData": {
                    object(ValueRange)
                  },
                }

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/update

        """
        spreadsheetid = self.spreadsheet_id

        majordimension = kwargs.get('majordimension', 'ROWS')
        valueinputoption = kwargs.get('valueinputoption', 'RAW')
        includevaluesinresponse = kwargs.get('includevaluesinresponse', False)
        responsevaluerenderoption = kwargs.get('responsevaluerenderoption', 'FORMATTED_VALUE')
        responsedatetimerenderoption = kwargs.get('responsedatetimerenderoption', 'SERIAL_NUMBER')

        dataframe = self.vet_input(dataframe)

        data = {
            "range": sheetrange,
            "majorDimension": majordimension,
            "values":
                [(dataframe.columns.values.tolist())] + (dataframe.values.tolist())
        }

        retry = 0
        while retry < 3:
            try:
                self.response = self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheetid,
                    range=sheetrange,
                    valueInputOption=valueinputoption,
                    includeValuesInResponse=includevaluesinresponse,
                    responseValueRenderOption=responsevaluerenderoption,
                    responseDateTimeRenderOption=responsedatetimerenderoption,
                    body=data).execute()
                print('update successful, retry # {0}'.format(retry))
                retry = 3
            except ConnectionAbortedError as e:
                log.error('ConnectionAbortedError {0}. Retry # {1}/3'.format(e, retry + 1))
                retry += 1
        if not self.response:
            log.info('Update Failed!')
        else:
            log.info('{0} Update Successful! '
                     'Response:\n{1}'.format(time.strftime("%Y-%m-%d %H:%M"), self.response))

    def batchUpdate(self,
                    datalist,
                    valueinputoption='RAW',
                    includevaluesinresponse=False,
                    responsevaluerenderoption='FORMATTED_VALUE',
                    responsedatetimerenderoption='SERIAL_NUMBER'):
        """Make multiple updates in one request

            Params:
                datalist (list):                    List of tuples (range, dataframe, majordim)
                                                    Ex: ('Sheet1', df, 'ROWS')


                valueinputoption (str):             How the input data should be interpreted.
                                                    Ex: 'USER_ENTERED'

                includevaluesinresponse (bool):     Determines if the update response should
                                                    include the values of the cells that were
                                                    updated.
                                                    Ex. False

                responsevaluerenderoption (str):    Determines how values in the response
                                                    should be rendered.
                                                    Ex: 'UNFORMATTED_VALUE'

                responsedatetimerenderoption (str): Determines how dates, times, and durations
                                                    in the response should be rendered. Ignored if
                                                    responseValueRenderOption is FORMATTED_VALUE.
                                                    Ex: 'FORMATTED_STRING'

            Returns:
                    {
                      "spreadsheetId": string,
                      "totalUpdatedRows": number,
                      "totalUpdatedColumns": number,
                      "totalUpdatedCells": number,
                      "totalUpdatedSheets": number,
                      "responses": [
                        {
                          object(UpdateValuesResponse)
                        }
                      ],
                    }

            https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/batchUpdate

            """

        spreadsheetid = self.spreadsheet_id
        data_list = [{"range": r,
                      "values": [(df.columns.values.tolist())] + (df.values.tolist()),
                      "majorDimension": majdim
                      } for (r, df, majdim) in datalist]
        data = {
            "valueInputOption": valueinputoption,
            "data": data_list,
            "includeValuesInResponse":includevaluesinresponse,
            "responseValueRenderOption":responsevaluerenderoption,
            "responseDateTimeRenderOption":responsedatetimerenderoption
        }
        self.response = self.service.spreadsheets().values().batchUpdate(
            spreadsheetId=spreadsheetid,
            body=data
        ).execute()
        if not self.response:
            log.info('Batch Update Failed!')
        else:
            log.info('{0} Batch Update Successful! '
                     'Response:\n{1}'.format(time.strftime("%Y-%m-%d %H:%M"), self.response))

    def clear(self, sheetrange):
        """Clear contents of sheetrange

        Params:
                sheetrange (str):     String referencing sheet range to clear
                                      Ex: 'Sheet1'

        """
        spreadsheetid = self.spreadsheet_id
        request = self.service.spreadsheets().values().clear(spreadsheetId=spreadsheetid,
                                                             range=sheetrange,
                                                             body={})
        response = request.execute()
        return(response)

    def batchClear(self, sheetranges):
        """Clear contents of a list of sheetranges

         Params:
                sheetranges (list):     List of strings referencing sheet ranges to clear
                                        Ex: ['Sheet1', 'Sheet2!A1:B4']

        """
        spreadsheetid = self.spreadsheet_id
        body = {'ranges': sheetranges}

        request = self.service.spreadsheets().values().batchClear(spreadsheetId=spreadsheetid,
                                                                  body=body)
        response = request.execute()
        return(response)

    def append(self,
               dataframe,
               sheetrange,
               majordimension='ROWS',
               valueinputoption='RAW',
               insertdataoption='INSERT_ROWS',
               includevaluesinresponse=False,
               responsevaluerenderoption='FORMATTED_VALUE',
               responsedatetimerenderoption='SERIAL_NUMBER'):
        """Append values to a spreadsheet

        Params:
            sheetrange (str): The A1 notation of a range to search for a logical table of data.
                              Values will be appended after the last row of the table,
                              Ex: 'Sheet1'
            valueinputoption (str): How the input data should be interpreted, Ex: 'USER_ENTERED'
            insertdataoption (str): How the input data should be inserted, Example 'OVERWRITE'
            includevaluesinresponse (bool): Determines if the update response should
                                            include the values of the cells that were appended
                                            Ex: False
            responsevaluerenderoption (str): Determines how values in the response should
                                             be rendered
                                             Ex: 'UNFORMATTED_VALUE'
            responsedatetimerenderoption (str): Determines how dates, times, and durations in
                                                the response should be rendered
                                                Ex: 'FORMATTED_STRING'

        Returns:
            response, returns response body in format:
                {
                  "spreadsheetId": string,
                  "tableRange": string,
                  "updates": {
                    object(UpdateValuesResponse)
                  },
                }

        https://developers.google.com/sheets/api/reference/rest/v4/spreadsheets.values/append

        """
        spreadsheetid = self.spreadsheet_id
        dataframe = self.vet_input(dataframe)
        data = {
            "range": sheetrange,
            "majorDimension": majordimension,
            "values": dataframe.values.tolist()
            #[(dataframe.columns.values.tolist())] + (dataframe.values.tolist())
        }
        self.response = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheetid,
            range=sheetrange,
            valueInputOption=valueinputoption,
            body=data
        ).execute()
        if not self.response:
            log.info('No data found.')
        else:
            log.info('{0} Append Successful! '
                     'Response:\n{1}'.format(time.strftime("%Y-%m-%d %H:%M"), self.response))

    def extract_sheet_names(self):
        pass

    def load_sheets(self, sheetslist, batch=None):
        data = {}
        if batch is None:
            batch = self.batchGet(sheetslist)
        for s in sheetslist:
            tmp = [value for key, value in batch.items() if s in key][0]
            if tmp is None:
                data[s] = tmp
            else:
                try:
                    data[s] = pd.DataFrame.from_records(tmp[1:len(tmp[1])],
                                                        columns=tmp[0][0:len(tmp[1])])
                except TypeError as err:
                    log.warning('Failed to load dataframe, '
                                'returning tmp.\n Error:\n\n{0}'.format(err))
                    data[s] = tmp
        return (data)
