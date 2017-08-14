
import sys
import json
import time
import random
import httplib2
import pandas as pd
import datetime as dt

from apiclient.http import MediaFileUpload
from apiclient.http import MediaIoBaseDownload
from apiclient.errors import HttpError

from prospecting.api import GoogleApi

from prospecting.errors import TooManyMetricsError, TooManyDimensionsError

import logging
log = logging.getLogger('prospecting.api')


class DriveApi(GoogleApi):
    """Class for DriveApi object


    https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/
    https://developers.google.com/apis-explorer/#p/drive/v3/

    """

    def __init__(self,
                 apiname='drive',
                 apiversion='v3',
                 scopelist=None):
        if scopelist is None:
            scopelist = ['https://www.googleapis.com/auth/drive.metadata.readonly']
        self.service = None
        self.data = {}  # store data from get requests
        self.files = []
        GoogleApi.__init__(self, apiname, apiversion, scopelist)
        pass

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)

    def list_files(self,
                   query,
                   corpusdomain='user',
                   space='drive',
                   pagesize=100,
                   orderby='name',
                   pagetoken=None):
        """Lists or searches files

        Params:
            query: string, A query for filtering the file results.
            corpus: string, The source of files to list.
                Allowed values:
                    'domain' - Files shared to the user's domain
                    'user' - Files owned by or shared to the user
            spaces: string, comma-separated list of spaces to query within the corpus.
                Allowed values:
                    'drive'
                    'appDataFolder'
                    'photos'
            pageSize: integer, The maximum number of files to return per page.
            orderBy: string, A comma-separated list of sort keys.
                Allowed values:
                    'createdTime', 'folder', 'modifiedByMeTime', 'modifiedTime',
                    'name', 'quotaBytesUsed', 'recency', 'sharedWithMeTime',
                    'starred', and 'viewedByMeTime'
            pageToken: string, The token for continuing a previous list request on the next page.
                This should be set to the value of 'nextPageToken' from the previous response.

        Returns:
            object

        """
        files = []
        log.info("Requesting files with {0}, {1}, {2}, {3}, {4}, {5}".format(
            query, corpusdomain, space, pagesize, orderby, pagetoken))
        while self.service:
            response = self.service.files().list(
                q=query,
                corpus=corpusdomain,
                spaces=space,
                orderBy=orderby,
                #fields='nextPageToken, files(id, name, mimeType)',
                pageSize=pagesize,
                pageToken=pagetoken
            ).execute()
            if response['files']:
                for file in response.get('files', []):
                    files.append(file)
                    """
                    filename = file.get('name')
                    fileid = file.get('id')
                    mimetype = file.get('mimeType')
                    print('Found file: {0} ({1}) {2}'.format(filename, fileid, mimetype))
                    """
                pagetoken = response.get('nextPageToken', None)
                if pagetoken is None:
                    log.info('File list received! Total files in list: {0}. '
                             'Check the class instance attribute `driveapiobject.files` '
                             'for file list.'.format(len(files)))
                    break
            else:
                log.info('No files found matching query:  {0}'.format(query))
                files = None
        return (files)

    def create(self,
               _body=None,
               mediabody=None,
               keeprevforever=None,
               usecontentasidxtxt=None,
               ignoredefvis=None,
               ocrlang=None):
        """
        Params:
            _body (object): The request body
            mediabody (str):    The filename of the media request body,
                                or an instance of a MediaUpload object.
            keeprevforever (bool):  Whether to set the 'keepForever' field in the new head
                                    revision. This is only applicable to files with binary
                                    content in Drive.
            usecontentasidxtxt (bool):  Whether to use the uploaded content as indexable text.
            ignoredefaultvis (bool):    Whether to ignore the domain's default visibility settings
                                        for the created file. Domain administrators can choose to
                                        make all uploaded files visible to the domain by default;
                                        this parameter bypasses that behavior for the request.
                                        Permissions are still inherited from parent folders.
            ocrlang (str):  A language hint for OCR processing during image
                            import (ISO 639-1 code).

        Returns:
            object

        https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#create

        """
        pass

    def get(self,
            fileid,
            ackabuse=None):
        """Get a file's metadata or content by ID

        Args:
            fileid: string, The ID of the file. (required)
            ackabuse: boolean, Whether the user is acknowledging the risk of downloading
                               known malware or other abusive files. This is only applicable
                               when alt=media.

        Returns:
            dict object

        https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#get

        """

        while self.service:
            response = self.service.files().get(
                fileId = fileid
            ).execute()
        return (response)

    def get_media(self,
                  fileid,
                  ackabuse=None):
        """Get a file's metadata or content by ID

        Args:
            fileid: string, The ID of the file. (required)
            ackabuse: boolean, Whether the user is acknowledging the risk of downloading
                               known malware or other abusive files. This is only applicable
                               when alt=media.

        Returns:
            The media object as a string.

        https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#get_media

        """
        pass

    def update(self,
               fileid,
               _body=None,
               mediabody=None,
               addparents=None,
               removeparents=None,
               usecontentasidxtxt=None,
               ignoredefvis=None,
               ocrlang=None):
        """Update a file's metadata and/or content with patch semantics.

        Params:
            fileid (str):    The ID of the file. (required)
            _body (object):   The request body
            mediabody (str):   The filename of the media request body, or an
                               instance of a MediaUpload object.
            addarents (str):   A comma-separated list of parent IDs to add.
            removeparents (str):   A comma-separated list of parent IDs to remove.
            usecontentasidxtxt (bool):  Whether to use the uploaded content as indexable text.
            ignoredefaultvis (bool):    Whether to ignore the domain's default visibility settings
                                        for the created file. Domain administrators can choose to
                                        make all uploaded files visible to the domain by default;
                                        this parameter bypasses that behavior for the request.
                                        Permissions are still inherited from parent folders.
            ocrlang (str):  A language hint for OCR processing during image
                            import (ISO 639-1 code).

        Returns:
            dict object

        https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#update

        """
        pass

    def copy(self,
             fileid,
             _body,
             keeprevforever=None,
             ignoredefvis=None,
             ocrlang=None):
        """Create a copy of a file and apply any requested updates with patch semantics.

        Params:
            fileid (str):   The ID of the file. (required)
            _body (object):    The request body. (required)
            keeprevforever (bool):   Whether to set the 'keepForever' field in the new head
                                     revision. This is only applicable to files with binary
                                     content in Drive.
            ignoredefvis (bool):  Whether to ignore the domain's default visibility settings
                                  for the created file. Domain administrators can choose to make
                                  all uploaded files visible to the domain by default;
                                  this parameter bypasses that behavior for the request.
                                  Permissions are still inherited from parent folders.
            ocrlang (str):    A language hint for OCR processing during image
                              import (ISO 639-1 code).

        Returns:
            object


        https://developers.google.com/resources/api-libraries/documentation/drive/v3/python/latest/drive_v3.files.html#copy

        """
        pass


class AnalyticsApi(GoogleApi):
    """Class for (Google) AnalyticsApi object

    https://developers.google.com/analytics/devguides/reporting/core/v4/

    Available Scopes:
        https://www.googleapis.com/auth/analytics
        https://www.googleapis.com/auth/analytics.readonly

    """

    request_template = {'viewId': '00000000',
                        'dateRanges': [{'startDate': str(dt.date.today() - dt.timedelta(weeks=1)),
                                        'endDate': str(dt.date.today() - dt.timedelta(days=1))}],
                        'metrics': [{'expression': 'ga:adCost'},
                                    {'expression': 'ga:impressions'},
                                    {'expression': 'ga:adClicks'}],
                        'dimensions': [{'name': 'ga:sourceMedium'},
                                       {'name': 'ga:campaign'},
                                       {'name': 'ga:adGroup'},
                                       {'name': 'ga:keyword'},
                                       {'name': 'ga:adMatchedQuery'}],
                        'dimensionFilterClauses': [
                            {'filters': [{'dimensionName': 'ga:sourceMedium',
                                          'operator': 'EXACT',
                                          'expressions': ['google / cpc']},],
                             'operator': 'AND'
                             }
                        ],
                        'samplingLevel': 'LARGE',
                        'pageSize': 10000}

    def __init__(self,
                 viewid,
                 apiname='analyticsreporting',
                 apiversion='v4',
                 scopelist=None):
        if viewid is None:
            log.error('Please provide a viewid, value of viewid provided is: {0}'.format(viewid))
            return
        if scopelist is None:
            scopelist = ['https://www.googleapis.com/auth/analytics.readonly']
        self.service = None
        self.view_id = viewid
        self.request = dict(AnalyticsApi.request_template)
        self.request['viewId'] = self.view_id

        discovery_url = 'https://analyticsreporting.googleapis.com/$discovery/rest'
        GoogleApi.__init__(self, apiname, apiversion, scopelist, discoveryurl=discovery_url)

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)

    def map_types_to_dtype(self, typelist):
        type_map = {'INTEGER': int,
                    'CURRENCY': float,
                    'PERCENT': float}
        return([type_map[t] for t in typelist])

    def init_request_template(self):
        self.request = dict(AnalyticsApi.request_template)

    def convert_to_dataframe(self, results):
        results_dict = {}
        for i, report in enumerate(results['reports']):

            try:
                data = [row['dimensions'] + row['metrics'][0]['values']
                        for row in report['data']['rows']]
                dim_cols = report['columnHeader']['dimensions']
            except Exception as err:
                data = [row['metrics'][0]['values'] for row in report['data']['rows']]
                dim_cols = []

            met_cols = [metric['name']
                        for metric
                        in report['columnHeader']['metricHeader']['metricHeaderEntries']]
            cols = [c.replace('ga:', '') for c in dim_cols + met_cols]

            dim_dtypes = [str for col in dim_cols]

            met_types = [metric['type']
                         for metric
                         in report['columnHeader']['metricHeader']['metricHeaderEntries']]
            met_dtypes = self.map_types_to_dtype(met_types)

            d_types = dim_dtypes + met_dtypes

            results_dict[i] = pd.DataFrame(data,
                                           columns=cols)

            # Convert column types
            for c, t in zip(cols, d_types):
                if c == 'date':
                    results_dict[i][c] = pd.to_datetime(results_dict[i][c], format='%Y%m%d')
                else:
                    results_dict[i][c] = results_dict[i][c].astype(t)

        return(results_dict)

    def batchGet(self,
                 start_date='7daysago',
                 end_date='yesterday',
                 metrics='ga:sessions,ga:users,ga:pageviews',
                 **kwargs):
        """tbd"""

        return_df = kwargs.get('return_df', True)
        page_size = kwargs.get('pageSize', 10000)
        #filters = kwargs.get('filters', None)
        dimensions = kwargs.get('dimensions', None)
        #include_empty_rows = kwargs.get('include_empty_rows', False)
        #sort = kwargs.get('sort', None)
        samplingLevel = kwargs.get('samplingLevel', 'LARGE')
        #segment = kwargs.get('segment', None)
        #start_index = kwargs.get('start_index', None)
        #output = kwargs.get('output', None)
        dimension_filters = kwargs.get('dimFilters', [])

        if len(metrics.split(',')) > 10:
            raise TooManyMetricsError(len(metrics.split(',')))
        else:
            metrics = [{'expression': metric} for metric in metrics.split(',')]

        if dimensions is not None:
            if len(dimensions.split(',')) > 7:
                raise TooManyDimensionsError(len(dimensions.split(',')))
            else:
                dimensions = [{'name': dim} for dim in dimensions.split(',')]

        results = self.service.reports().batchGet(
            body={
                'reportRequests': [
                    {'viewId': self.view_id,
                     'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
                     'dimensionFilterClauses': dimension_filters,
                     'samplingLevel': samplingLevel,
                     'metrics': metrics,
                     'dimensions': dimensions,
                     'pageSize': page_size
                     },
                ]
            }).execute()
        if return_df is True:
            results = self.convert_to_dataframe(results)
        return(results)

        def run_regex_sequence(self, regexset):

            index_sets = {}
            for regex in regexset:

                index_sets[str(regex)] = ''
                pass


class SearchConsoleApi(GoogleApi):
    """Class for (Google) SearchConsoleApi object



    Available Scopes:
        https://www.googleapis.com/auth/webmasters
        https://www.googleapis.com/auth/webmasters.readonly

    """
    request_template = {'startDate': str(dt.date.today() - dt.timedelta(weeks=1)),
                        'endDate': str(dt.date.today() - dt.timedelta(days=1)),
                        'dimensions': ['query', 'page', 'device'],
                        'rowLimit': 5000
                        }

    def __init__(self,
                 propertyurl,
                 apiname='webmasters',
                 apiversion='v3',
                 scopelist=None):
        if propertyurl is None:
            raise Exception('propertyurl is required')
        if scopelist is None:
            scopelist = ['https://www.googleapis.com/auth/webmasters.readonly']

        self.property_url = propertyurl
        self.request = dict(SearchConsoleApi.request_template)

        GoogleApi.__init__(self, apiname, apiversion, scopelist)

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)

    def convert_to_dataframe(self, request, response, drop_key, convert_date):
        tmp_df = pd.DataFrame(response['rows'])
        tmp_df[request['dimensions']] = tmp_df['keys'].apply(pd.Series)
        if drop_key is True:
            tmp_df = tmp_df.drop('keys', axis=1)
        if convert_date is True:
            if 'date' in tmp_df.columns:
                tmp_df['date'] = pd.to_datetime(tmp_df['date'], format='%Y-%m-%d')
        return(tmp_df)

    def sitesList(self):
        pass

    def sitesGet(self):
        pass

    def sitesAdd(self):
        pass

    def sitesDelete(self):
        pass

    def query(self, request=None, **kwargs):
        return_df = kwargs.get('return_df', True)
        drop_keys_col = kwargs.get('drop_keys_col', True)
        convert_date_col = kwargs.get('convert_date_col', True)

        if request is None:
            request = self.request

        response = self.service.searchanalytics().query(
            siteUrl=self.property_url,
            body=request
        ).execute()

        if 'rows' in response:
            if return_df is True:
                response = self.convert_to_dataframe(
                    request,
                    response,
                    drop_keys_col,
                    convert_date_col
                )
            return(response)
        else:
            log.error('No data returned for dates provided.')

    def batchQuery(self, startdate=None, enddate=None, request=None, **kwargs):

        response = self.service.searchanalytics().query(
            siteUrl=self.property_url,
            body=request
        ).execute()
        return(response)

    def getSitemap(self):
        pass

    def listSitemap(self):
        pass

    def submitSitemap(self):
        pass

    def deleteSitemap(self):
        pass

    def queryCrawlErrors(self):
        self.response = self.service.urlcrawlerrorscounts().query(
            siteUrl=self.property_url
        ).execute()
        return(self.response)

    def getCrawlErrors(self):
        log.info('getCrawlErrors not yet implemented.')
        #self.response = self.service.urlcrawlerrorssamples().get(
        #    siteUrl=self.property_url
        #).execute()
        #return(self.response)
        pass

    def listCrawlErrors(self):
        log.info('listCrawlErrors not yet implemented.')
        #self.response = self.service.urlcrawlerrorssamples().list(
        #    siteUrl=self.property_url
        #).execute()
        #return(self.response)
        pass

    def markFixedCrawlErrors(self):
        log.info('markFixedCrawlErrors not yet implemented.')
        #self.response = self.service.urlcrawlerrorssamples().markAsFixed(
        #    siteUrl=self.property_url
        #).execute()
        #return(self.response)
        pass

    def crawlErrors(self):

        def markAsFixed():
            self.response = self.service.urlcrawlerrorssamples().markAsFixed(
                siteUrl=self.property_url
            ).execute()
            pass


class StorageApi(GoogleApi):
    """Class for (Google) StorageApi object

    https://cloud.google.com/storage/docs/json_api/v1/

    """

    def __init__(self,
                 apiname='storage',
                 apiversion='v1',
                 scopelist=None):
        if scopelist is None:
            scopelist = ['https://www.googleapis.com/auth/devstorage.read_only']
        self.RETRYABLE_ERRORS = (httplib2.HttpLib2Error, IOError)
        self.NUM_RETRIES = 5
        self.CHUNKSIZE = 2 * 1024 * 1024
        self.DEFAULT_MIMETYPE = 'application/octet-stream'
        GoogleApi.__init__(self, apiname, apiversion, scopelist)
        pass

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)

    def handle_progressless_iter(self, error, progressless_iters):
        if progressless_iters > self.NUM_RETRIES:
            print('Failed to make progress for too many consecutive iterations.')
            raise error

        sleeptime = random.random() * (2**progressless_iters)
        log.info('Caught exception ({0}). '
                 'Sleeping for {1} seconds '
                 'before retry #{2}.'.format(str(error),
                                             sleeptime,
                                             progressless_iters))
        time.sleep(sleeptime)

    def print_with_carriage_return(self, s):
        sys.stdout.write('\r' + s)
        sys.stdout.flush()

    def upload(self, argv):
        filename = argv[1]
        bucket_name, object_name = argv[2][5:].split('/', 1)
        assert bucket_name and object_name

        #service = get_authenticated_service(RW_SCOPE)

        log.info('Building upload request...')
        media = MediaFileUpload(filename,
                                chunksize=self.CHUNKSIZE,
                                resumable=True)
        if not media.mimetype():
            media = MediaFileUpload(filename,
                                    self.DEFAULT_MIMETYPE,
                                    resumable=True)
        request = self.service.objects().insert(bucket=bucket_name,
                                                name=object_name,
                                                media_body=media)

        log.info('Uploading file: %s to bucket: %s object: %s ' % (filename,
                                                                   bucket_name,
                                                                   object_name))

        progressless_iters = 0
        response = None
        while response is None:
            error = None
            try:
                progress, response = request.next_chunk()
                if progress:
                    #self.print_with_carriage_return('Upload %d%%' % (100 * progress.progress()))
                    self.print_with_carriage_return('Upload {:d}'.format(
                        100 * progress.progress())
                    )
            except HttpError as err:
                error = err
                if err.resp.status < 500:
                    raise
            except self.RETRYABLE_ERRORS as err:
                error = err

            if error:
                progressless_iters += 1
                self.handle_progressless_iter(error, progressless_iters)
            else:
                progressless_iters = 0
        log.info('\nUpload complete!')
        log.info('Uploaded Object:')
        log.info(json.dumps(response, indent=2))

    def download(self, argv):
        bucket_name, object_name = argv[1][5:].split('/', 1)
        filename = argv[2]
        assert bucket_name and object_name

        #service = get_authenticated_service(RO_SCOPE)

        log.info('Building download request...')
        request = self.service.objects().get_media(bucket=bucket_name,
                                                   object=object_name)
        with open(filename, 'w') as f:
            media = MediaIoBaseDownload(f,
                                        request,
                                        chunksize=self.CHUNKSIZE)
            log.info('Downloading bucket: {0} object: {1} to file: {2}'.format(bucket_name,
                                                                               object_name,
                                                                               filename))
            progressless_iters = 0
            done = False
            while not done:
                error = None
                try:
                    progress, done = media.next_chunk()
                    if progress:
                        self.print_with_carriage_return('Download {:d}'.format(
                            int(progress.progress() * 100))
                        )
                except HttpError as err:
                    error = err
                    if err.resp.status < 500:
                        raise
                except self.RETRYABLE_ERRORS as err:
                    error = err
                if error:
                    progressless_iters += 1
                    self.handle_progressless_iter(error, progressless_iters)
                else:
                    progressless_iters = 0
        log.info('\nDownload complete!')


class FusionTableApi(GoogleApi):
    """Class for FusionTableApi object


    https://developers.google.com/fusiontables/docs/v2/reference/

    """

    def __init__(self,
                 apiname='fusiontables',
                 apiversion='v2',
                 scopelist=None):
        if scopelist is None:
            scopelist = ['https://www.googleapis.com/auth/fusiontables']

        self.info = None  # reserved for metadata

        GoogleApi.__init__(self, apiname, apiversion, scopelist)
        pass

    def authenticate(self):
        self.service = GoogleApi.authenticate(self)
