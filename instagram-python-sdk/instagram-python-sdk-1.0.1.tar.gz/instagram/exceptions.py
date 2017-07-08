class InstagramException(Exception):
    status_code = None
    api_code = None
    message = None
    error_type = None
    response = None

    def __init__(self, code, response):
        self.status_code = code
        self.response = response

        if 'error_type' in response:
            self.error_type = response['error_type']
            self.message = response['error_message']
            self.api_code = response['code']
