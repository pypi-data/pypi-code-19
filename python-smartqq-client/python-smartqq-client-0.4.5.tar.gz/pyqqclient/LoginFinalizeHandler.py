from requests import Response
from .LoginStepHandler import LoginStepHandler
from .OnlineChecker import OnlineChecker


class LoginFinalizeHandler(LoginStepHandler):
    def next_step(self, accumulated, last_response: Response) -> ({}, Response):
        del accumulated["login_barcode"]
        del accumulated["login_success_url"]
        resp = OnlineChecker.check_online(accumulated, self.session)
        print(resp)
        return accumulated, resp
