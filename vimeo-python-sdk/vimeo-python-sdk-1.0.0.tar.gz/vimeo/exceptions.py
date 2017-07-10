class VimeoException(Exception):
    status_code = None
    api_code = None
    message = None
    response = None

    def __init__(self, code, response):
        self.status_code = code
        self.response = response

        if 'error' in response:
            self.message = response['error']
            self.api_code = code
