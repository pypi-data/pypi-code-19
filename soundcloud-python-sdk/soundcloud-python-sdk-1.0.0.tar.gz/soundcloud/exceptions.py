class SoundCloudException(Exception):
    status_code = None
    api_code = None
    message = None
    response = None

    def __init__(self, code, response):
        self.status_code = code
        self.response = response

        if 'errors' in response:
            self.api_code = code
            self.message = response['errors'][0]['error_message']
