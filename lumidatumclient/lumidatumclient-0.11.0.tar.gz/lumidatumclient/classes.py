import collections
import json
import os

import requests
import requests_toolbelt

import helpers


class LumidatumClient(object):

    def __init__(self, authentication_token, model_id=None, host_address='https://www.lumidatum.com'):
        self.authentication_token = authentication_token
        self.model_id = str(model_id)
        self.host_address = host_address.rstrip('/')


    def getSegmentation(self, parameters='', model_id=None, deserialize_response=True):

        return self.api(http_method='POST', parameters=parameters, model_id=model_id, api_function='segmentation', deserialize_response=deserialize_response)

    def getLifetimeValue(self, parameters, model_id=None, deserialize_response=True):

        return self.api(http_method='POST', parameters=parameters, model_id=model_id, api_function='customervalue', deserialize_response=deserialize_response)

    def getRecommendations(self, parameters, model_id=None, deserialize_response=True):
        """
        Get recommendations for a model specified by model_id.

        Returns a list of id/score pairs in descending order from the highest score.
        """

        return self.api(http_method='POST', parameters=parameters, model_id=model_id, api_function='predict', deserialize_response=deserialize_response)

    def getRecommendationDescriptions(self, parameters, model_id=None, deserialize_response=True):
        """
        Get human readable recommendations.
        """
        parameters = dict(parameters)
        parameters['human_readable'] = True

        return self.api(http_method='POST', parameters=parameters, model_id=model_id, api_function='predict', deserialize_response=deserialize_response)

    def api(self, http_method='POST', parameters={}, model_id=None, api_function='predict', deserialize_response=True):
        """
        General method for the Lumidatum REST API.

        If deserialize_response is set to False, a requests.HttpResponse object will be returned.
        """

        selected_model_id = str(model_id) if model_id else self.model_id
        if selected_model_id is None:
            raise ValueError('model_id must be specified either at initialization of LumidatumClient or in client method call.')

        headers = {
            'Authorization': self.authentication_token,
            'content-type': 'application/json',
        }

        api_endpoint = '{}/api/{}/{}'.format(self.host_address, api_function, selected_model_id)

        if http_method == 'POST':
            response = requests.post(
                api_endpoint,
                json.dumps(parameters),
                headers=headers
            )
        elif http_method == 'GET':
            response = requests.get(
                api_endpoint,
                headers=headers
            )
        else:
            raise ValueError('HTTP method "{}" not allowed'.format(http_method))

        if deserialize_response:
            try:

                return response.json()
            except:

                return {'error': response.text}
        else:

            return response


    # Data string takes priority, in the case of data_string and file_path params both being provided
    def sendUserData(self, data_string=None, file_path=None, model_id=None, file_upload_status_to_std_out=True):

        return self.dataUpdateApi(model_id, 'users', data_string, file_path, file_upload_status_to_std_out)

    def sendItemData(self, data_string=None, file_path=None, model_id=None, file_upload_status_to_std_out=True):

        return self.dataUpdateApi(model_id, 'items', data_string, file_path, file_upload_status_to_std_out)

    def sendTransactionData(self, data_string=None, file_path=None, model_id=None, file_upload_status_to_std_out=True):

        return self.dataUpdateApi(model_id, 'transactions', data_string, file_path, file_upload_status_to_std_out)

    def sendFeedbackData(self, data_string=None, file_path=None, model_id=None, file_upload_status_to_std_out=True):

        return self.dataUpdateApi(model_id, 'feedback', data_string, file_path, file_upload_status_to_std_out)

    def dataUpdateApi(self, model_id, data_type, data_string, file_path, file_upload_status_to_std_out):
        selected_model_id = str(model_id) if model_id else self.model_id

        if selected_model_id is None:
            raise ValueError('model_id must be specified either at initialization of LumidatumClient or in client method call.')

        if data_string:
            response = requests.post(
                '{}/api/data?model_id={}&data_type={}'.format(self.host_address, selected_model_id, data_type),
                data_string,
                headers={
                    'content-type': 'application/json',
                    'authorization': self.authentication_token,
                }
            )

            return response
        elif file_path:
            file_size = os.stat(file_path).st_size
            file_name = os.path.basename(file_path)

            presign_response = requests.post(
                '{}/api/data'.format(self.host_address),
                headers={
                    'content-type': 'application/json', # Do I need this?
                    'authorization': self.authentication_token,
                },
                data=json.dumps({
                    'model_id': selected_model_id,
                    'data_type': data_type,
                    'file_name': file_name,
                    'file_size': file_size,
                })
            )
            presign_response_object = helpers.parsePresignResponse(presign_response)

            upload_response = self.sendFile(presign_response_object, file_path, file_upload_status_to_std_out)

            return upload_response
        else:
            raise ValueError('Missing argument: data_string or file_path required')

    def sendFile(self, presign_response_object, file_path, file_upload_status_to_std_out):
        with open(file_path, 'rb') as upload_file:
            destination_url = presign_response_object['url']
            fields = collections.OrderedDict(presign_response_object['fields'])
            fields['file'] = upload_file

            multipart_encoded_data  = requests_toolbelt.multipart.encoder.MultipartEncoder(fields=fields)

            response = requests.post(destination_url, data=multipart_encoded_data, headers={'Content-Type': multipart_encoded_data.content_type})

        return response

    def getLTVReportDates(self, sub_type=None, model_id=None, zipped=False, latest=False):

        return self.getAvailableReports('LTV', sub_type, model_id, zipped=zipped, latest=latest, return_dates=True)

    def getLatestLTVReport(self, download_file_path, sub_type=None, model_id=None, zipped=True, stream_download=True):
        latest_report_key_name = self.getAvailableReports('LTV', sub_type, model_id, zipped)

        return self.getReport(latest_report_key_name, download_file_path, model_id, stream_download=stream_download)

    def getSegmentationReportDates(self, sub_type=None, model_id=None, zipped=False, latest=False):

        return self.getAvailableReports('SEG', sub_type, model_id, zipped=zipped, latest=latest, return_dates=True)

    def getLatestSegmentationReport(self, download_file_path, sub_type=None, zipped=True, model_id=None, stream_download=True):
        latest_report_key_name = self.getAvailableReports('SEG', sub_type, model_id, zipped)

        return self.getReport(latest_report_key_name, download_file_path, model_id, stream_download=stream_download)

    def getAvailableReports(self, report_type, sub_type, model_id, zipped=True, latest=True, return_dates=False):
        selected_model_id = str(model_id) if model_id else self.model_id

        list_reports_response = requests.get(
            '{}/api/data?model_id={}&report_type={}&sub_type={}&zipped={}&latest={}&return_dates={}'.format(
                self.host_address,
                selected_model_id,
                report_type,
                sub_type,
                zipped,
                latest,
                return_dates
            ),
            headers={
                'content-type': 'application/json',
                'authorization': self.authentication_token,
            }
        )

        list_reports_response.raise_for_status()
        list_reports_response_object = list_reports_response.json()

        if return_dates and list_reports_response_object.get('latest_report_timestamp'):

            return list_reports_response_object.get('latest_report_timestamp')
        elif return_dates and list_reports_response_object.get('report_timestamps'):

            return list_reports_response_object.get('report_timestamps')

        if list_reports_response_object.get('latest_key_name'):

            return list_reports_response_object.get('latest_key_name')
        else:

            return list_reports_response_object.get('available_key_names')

    def getReport(self, key_name, download_file_path, model_id, stream_download=True):
        selected_model_id = str(model_id) if model_id else self.model_id

        presign_response = requests.post(
            '{}/api/data'.format(self.host_address),
            headers={
                'content-type': 'application/json',
                'authorization': self.authentication_token,
            },
            data=json.dumps({
                'model_id': selected_model_id,
                'key_name': key_name,
                'is_download': True,
            })
        )

        presigned_response_object = helpers.parsePresignResponse(presign_response)

        download_response = self.downloadFile(download_file_path, presigned_response_object, stream_download)

        return download_response

    def downloadFile(self, download_file_path, presigned_response_object, stream_download):
        with open(download_file_path, 'wb') as download_file:
            response = requests.get(presigned_response_object.get('url'), stream=stream_download)
            response.raise_for_status()

            if stream_download:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        download_file.write(chunk)
            else:
                download_file.write(response.text)

        return response
