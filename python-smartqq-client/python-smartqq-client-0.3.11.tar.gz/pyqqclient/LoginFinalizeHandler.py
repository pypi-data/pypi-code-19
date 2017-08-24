from requests import Response
from .LoginStepHandler import LoginStepHandler


class LoginFinalizeHandler(LoginStepHandler):
    def next_step(self, accumulated, last_response: Response) -> ({}, Response):
        del accumulated["login_barcode"]
        del accumulated["login_success_url"]
        return accumulated, last_response
