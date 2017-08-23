# http://yaml.org/type/bool.html + 1 and 0

TRUES = {
    'y', 'yes',
    't', 'true',
    'on',
    '1',
}

FALSES = {
    'n', 'no',
    'f', 'false',
    'off',
    '0',
}

def to_bool(s, default=None):
    if not s:
        return default

    s = s.lower()
    if s in TRUES:
        return True
    if s in FALSES:
        return False
    raise ValueError('Value not convertible to bool')
