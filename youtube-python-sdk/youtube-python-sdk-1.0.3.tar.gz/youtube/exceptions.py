class YouTubeException(Exception):
    def __init__(self, code, message, response):
        self.status_code = code
        self.message = message
        self.response = response
