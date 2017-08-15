from urllib.parse import quote_plus, unquote


def dict_to_query_string(d):
    """Helper to serialize URL-safe parameters into a string."""
    pairs = list()
    for name in d:
        pairs.append('='.join([
            quote_plus(name),
            quote_plus(d[name]),
        ]))
    return '&'.join(pairs)


def uri_to_query_string_params(uri):
    """Helper to deserialize query string into a dictionary.

    Args:
        uri: expects a uri that starts with https?:// or /.
    """
    output = dict()
    if '?' not in uri:
        return output
    qs = uri[uri.find('?')+1:].split('#')[0]
    pairs = qs.split('&')
    for pair in pairs:
        if '=' not in pair:
            output[unquote(pair)] = True
            continue
        elems = pair.split('=')
        output[unquote(elems[0])] = unquote(elems[1])
    return output
