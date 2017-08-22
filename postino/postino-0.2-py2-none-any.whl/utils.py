def to_unicode(text, encoding, errors):
    if isinstance(text, unicode):
        return text
    elif isinstance(text, str):
        return unicode(text, encoding, errors)
    else:
        return unicode(text)
