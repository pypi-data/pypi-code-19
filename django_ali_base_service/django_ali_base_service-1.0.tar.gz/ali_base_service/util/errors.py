from django.utils.translation import ugettext as _

error_list = {
    101: {
        "sub_code": 101,
        "message": _("Does not exist"),
        "args": None
    },
    111: {
        "sub_code": 111,
        "message": _("Session is invalid/expired."),
        "args": None
    },
    116: {
        "sub_code": 116,
        "message": _("Following parameters have invalid values."),
        "args": None
    },
    117: {
        "sub_code": 117,
        "message": _('Following parameters are missing.'),
        "args": None
    },
    118: {
        "sub_code": 118,
        "message": _('Bad JSON'),
        "args": None
    },
    120: {
        "sub_code": 120,
        "message": _('Invalid basic header.'),
        "args": None
    },
    123: {
        "sub_code": 123,
        "message": _('User already exist.'),
        "args": None
    }
}


def get_error(error_code, args=None):
    error = error_list[error_code]

    if args is not None:
        error["args"] = args

    return error


def get_error_message(error_code):
    return error_list[error_code]["message"]

