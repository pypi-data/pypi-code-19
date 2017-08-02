import logging


def debugit(issuer=None, message=None):
    logging.debug('{}: {}'.format(issuer, message))


def bad_value(issuer=None, message=None, value=None):
    logging.debug('{}: **ERROR** Passed a bad value: {}'.format(issuer, value))
    exception_message = '{}: {}'.format(issuer, message)
    raise ValueError(exception_message)

#    raise ValueError('{}: A hex digit must be a string representation or integer '
#                     'of a number between 0 (zero) and F (fifteen).')
