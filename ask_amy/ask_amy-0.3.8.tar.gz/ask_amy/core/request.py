import logging

from ask_amy.core.object_dictionary import ObjectDictionary

logger = logging.getLogger()


class Request(ObjectDictionary):
    def __init__(self, request_dict):
        super().__init__(request_dict)

    def _request_type(self):
        return self.get_value_from_dict(['type'])

    request_type = property(_request_type)

    def _request_id(self):
        return self.get_value_from_dict(['requestId'])

    request_id = property(_request_id)

    def _locale(self):
        return self.get_value_from_dict(['locale'])

    locale = property(_locale)

    def _timestamp(self):
        return self.get_value_from_dict(['timestamp'])

    timestamp = property(_timestamp)

    def _attributes(self):
        has_attributes = self.get_value_from_dict(['attributes'])
        if has_attributes is None:
            self._obj_dict['attributes'] = {}
        return self._obj_dict['attributes']

    attributes = property(_attributes)

    def attribute_exists(self, attribute):
        if attribute in self.attributes.keys():
            return True
        else:
            return False

    @staticmethod
    def factory(request_dict):
        logger.debug("**************** entering Request.factory")
        request_type = request_dict['type']
        if request_type == "LaunchRequest": return LaunchRequest(request_dict)
        if request_type == "IntentRequest": return IntentRequest(request_dict)
        if request_type == "SessionEndedRequest": return SessionEndedRequest(request_dict)
        assert 0, "Bad Request creation: " + request_type


class LaunchRequest(Request):
    def __init__(self, request_dict):
        super().__init__(request_dict)


class IntentRequest(Request):
    CONFIRMATION_STATUSES = ['NONE', 'CONFIRMED', 'DENIED']
    DIALOG_STATES = ['STARTED', 'IN_PROGRESS', 'COMPLETED']

    def __init__(self, request_dict):
        super().__init__(request_dict)
        self._slots = None

    def _dialog_state(self):
        return self.get_value_from_dict(['dialogState'])

    dialog_state = property(_dialog_state)

    def _intent_name(self):
        return self.get_value_from_dict(['intent', 'name'])

    intent_name = property(_intent_name)

    def _confirmation_status(self):
        return self.get_value_from_dict(['intent', 'confirmationStatus'])

    confirmation_status = property(_confirmation_status)

    def _get_slots(self):
        if self._slots is None:
            self._slots = {}
            slots_dict = self.get_value_from_dict(['intent', 'slots'])
            if slots_dict is not None:
                for slot_name in slots_dict.keys():
                    self._slots[slot_name] = Slot(slots_dict[slot_name])
        return self._slots

    slots = property(_get_slots)

    def value_for_slot_name(self, name):
        path = ['intent', 'slots', name, 'value']
        return self.get_value_from_dict(path)


class SessionEndedRequest(Request):
    REASONS = ['USER_INITIATED', 'ERROR', 'EXCEEDED_MAX_REPROMPTS']
    ERROR_TYPES = ['INVALID_RESPONSE', 'DEVICE_COMMUNICATION_ERROR', 'INTERNAL_ERROR']

    def __init__(self, request_dict):
        super().__init__(request_dict)

    def _reason(self):
        return self.get_value_from_dict(['reason'])

    reason = property(_reason)

    def _error_type(self):
        return self.get_value_from_dict(['error', 'type'])

    error_type = property(_error_type)

    def _error_message(self):
        return self.get_value_from_dict(['error', 'message'])

    error_message = property(_error_message)


class Slot(ObjectDictionary):
    CONFIRMATION = ['NONE', 'CONFIRMED', 'DENIED']

    def __init__(self, slot_dict):
        super().__init__(slot_dict)

    def _name(self):
        return self.get_value_from_dict(['name'])

    name = property(_name)

    def _value(self):
        return self.get_value_from_dict(['value'])

    value = property(_value)

    def _confirmation_status(self):
        return self.get_value_from_dict(['confirmationStatus'])

    confirmation_status = property(_confirmation_status)
