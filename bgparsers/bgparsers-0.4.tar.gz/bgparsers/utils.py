
def dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s


def chunkizator(iterable, size=1000):
    """
    Creates chunks from an iterable

    Args:
        iterable:
        size (int): elements in the chunk

    Returns:
        list. Chunk

    """
    s = 0
    chunk = []
    for i in iterable:
        if s == size:
            yield chunk
            chunk = []
            s = 0
        chunk.append(i)
        s += 1
    yield chunk