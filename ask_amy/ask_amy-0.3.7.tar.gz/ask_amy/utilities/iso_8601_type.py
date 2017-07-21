import logging

logger = logging.getLogger()


class ISO8601_Validator(object):
    @staticmethod
    def is_valid_value(value, iso_type):
        status = -1
        message = ""
        if iso_type == 'AMAZON.NUMBER':
            try:
                int(value)
                status = 0
            except ValueError:
                logger.debug("Value in slot not a valid AMAZON.NUMBER")
                message = "i did not understand the number"

        if iso_type == 'AMAZON.TIME':
            if ':' in value:
                hours_str, minutes_str = value.split(':')
                try:
                    hours = int(hours_str)
                    minutes = int(minutes_str)
                    if 0 <= hours <= 23 and 0 <= minutes <= 59:
                        status = 0
                except ValueError:
                    logger.debug("Value in slot not a valid AMAZON.TIME")
                    message = "i did not understand the time"

            elif value in ['NI', 'MO', 'AF', 'EV']:
                status = 0
        return status, message
