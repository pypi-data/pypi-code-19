from .exceptions import BadInputException, InvalidAuthentication, InternalServerError
from .nimble_code import NimbleCodes
from .settings import SIEBEL_GATEWAY_URL, SUCCESS_CODES
from django.http import QueryDict
import requests
import json


# This class was created in order to extract functionality from nimble microservices
class NimbleHelper:
    @staticmethod
    def cut_response_hierarchy(hierarchy, response):
        hierarchy_list = hierarchy.split('.')
        try:
            for hierarchy_level in hierarchy_list:
                if hierarchy_level == '0':
                    response = response[int(hierarchy_level)]
                else:
                    response = response[hierarchy_level]
        except (KeyError, TypeError):
            response = []
        return response

    # Checks Request For HTTP_X_CONSUMER_ID header (indicates kong has authorized the request)
    @staticmethod
    def check_authorization(request):
        x_consumer_id = request.META.get('HTTP_X_CONSUMER_ID', None)
        if not x_consumer_id:
            raise InvalidAuthentication
        return x_consumer_id

    @classmethod
    def run_siebel_request(cls, x_consumer_id, params, soap_action):
        data = json.dumps({"soapaction": soap_action, "data": params})
        headers = {"X_Consumer_ID": x_consumer_id, "Content-Type": "application/json"}
        try:
            results = requests.post(SIEBEL_GATEWAY_URL, data=data, headers=headers)
        except ConnectionError as exception:
            raise InternalServerError(str(exception))
        return json.loads(results.content.decode("utf-8"))

    # Checks the required fields in a tuple [('name',), ('id',)] will be checked in a "AND" format,
    # if multiple values in a tuple e.g. [('name', 'id',)] these will be treated as 'OR' conditionals
    @staticmethod
    def check_required_input(required_fields, call_values):
        try:
            for fields in required_fields:
                check = False
                for field in fields:
                    if call_values['data'][field]:
                        check = True
                if not check:
                    raise BadInputException
        except KeyError:
            raise BadInputException
        return True

    @classmethod
    def request_manager(cls, soap_action, params, x_consumer_id, hierarchy):
        response = cls.run_siebel_request(x_consumer_id=x_consumer_id, params=params, soap_action=soap_action)
        if response['status'] in SUCCESS_CODES:
            response = cls.cut_response_hierarchy(hierarchy=hierarchy, response=response)
            return NimbleCodes.http_code_helper(code=200, data=response)
        else:
            return NimbleCodes.http_code_helper(code=response["status"], message=response["message"])

    # These functions get data from a request passed through
    # ==============================================================================================
    # START OF FUNCTIONS
    # ==============================================================================================
    # Takes in a fields argument (list of tuples) in order to map request variables to a dict, pass
    # through required_fields in order to have required fields add the names as tuples to the required_fields list

    # USED FOR GET REQUESTS
    @classmethod
    def check_get_parameters(cls, request, fields, required_fields=None, pk=None):
        call_values = {
            'x_consumer_id': cls.check_authorization(request),
            'data': {}
        }
        for field in fields:
            parameter, value = field
            if pk and value == "pk":
                call_values['data'][parameter] = pk
            else:
                call_values['data'][parameter] = request.GET.get(value, None)
        cls.check_required_input(required_fields, call_values)
        return call_values

    # USED FOR POST REQUESTS
    @classmethod
    def check_post_parameters(cls, request, fields, required_fields):
        call_values = {
            'x_consumer_id': cls.check_authorization(request),
            'data': {}
        }
        for field in fields:
            parameter, value = field
            call_values['data'][parameter] = request.POST.get(value, None)
        cls.check_required_input(required_fields, call_values)
        return call_values

    # USED FOR PUT REQUESTS
    @classmethod
    def check_put_parameters(cls, request, fields, required_fields, pk):
        call_values = {
            'x_consumer_id': cls.check_authorization(request),
            'data': {}
        }
        put = QueryDict(request.body)
        for field in fields:
            parameter, value = field
            if pk and value == "pk":
                call_values['data'][parameter] = pk
            else:
                call_values['data'][parameter] = put.get(value, None)
        cls.check_required_input(required_fields, call_values)
        return call_values
    # ==============================================================================================
    # END OF FUNCTIONS
    # ==============================================================================================
