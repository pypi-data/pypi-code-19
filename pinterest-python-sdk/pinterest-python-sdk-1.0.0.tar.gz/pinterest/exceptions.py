class PinterestException(Exception):
    status_code = None
    api_code = None
    message = None
    response = None

    def __init__(self, code, response):
        self.status_code = code
        self.response = response

        if 'status' in response and response['status'] == 'failure':
            self.api_code = response['code']
            self.message = response['message']
