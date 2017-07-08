def collection(validators, required=False):
    def __init__(self, validators, required=False):
        self.validators = validators if type(validators) is list else [validators]
