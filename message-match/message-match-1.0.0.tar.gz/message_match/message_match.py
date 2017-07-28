
def mmatch(message, match):
    if not isinstance(message, dict):
        raise Exception('first argument, message, must be a dict type')
    if not isinstance(match, dict):
        raise Exception('second argument, match, must be a dict type')
    return _mmatch(message, match)


def _mmatch(message, match):
    if isinstance(message, dict) and isinstance(match, dict):
        for key in match:
            if key not in message:
                return False
            sub_message = message[key]
            sub_match = match[key]
            if not _mmatch(sub_message, sub_match):
                return False
        return True
    if isinstance(message, list) and isinstance(match, list):
        # print("do list/list check")
        return False

    # first check to see if it starts with ' special' and handle that
    return(message == match)
