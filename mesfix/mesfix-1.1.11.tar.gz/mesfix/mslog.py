import time


class LogMessage(object):
    INFO = "INFO"
    ERROR = "ERROR"

    def __init__(self, microservice):
        self.microservice = microservice

    def info(self, transaction_id, entity_id, profile_id, description):
        return self.message(self.INFO, transaction_id, entity_id, profile_id, description)

    def error(self, transaction_id, entity_id, profile_id, description):
        return self.message(self.ERROR, transaction_id, entity_id, profile_id, description)

    def message(self, log_type, transaction_id, entity_id, profile_id, description):
        message = {
            'timestamp': int(round(time.time() * 1000)),
            'logType': log_type,
            'transaction': transaction_id,
            'description': description,
            'microservice': self.microservice,
            'entity': entity_id,
            'profile': profile_id
        }

        return message
