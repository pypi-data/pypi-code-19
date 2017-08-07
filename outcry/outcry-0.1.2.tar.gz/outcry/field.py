from outcry.exceptions import OutcryUnexpectedTypeError
from outcry.param import Param 

        
class Field(Param):
    pass


def field(validators=None, required=False):
    return Field(validators=validators, required=required)

