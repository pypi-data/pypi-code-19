import json
from rinzler.exceptions.invalid_input_exception import InvalidInputException

class BaseService(object):

    __payload = dict()
    __jwt_data = dict()
    __jwt = str()

    def __init__(self):
        pass

    def set_payload(self, payload: dict()):
        try:
            self.__payload = json.loads(payload)
        except Exception as e:
            print(e)
            raise InvalidInputException("JSON inválido ou mal-formatado.")
        return self

    def get_payload(self):
        return self.__payload

    def set_jwt_data(self, jwt_data: dict()):
        self.__jwt_data = jwt_data
        return self

    def get_jwt_data(self):
        return self.__jwt_data

    def set_jwt(self, token: str()):
        self.__jwt = token
        return self

    def get_jwt(self):
        return self.__jwt
