import random
import string


def random_alphanum(length):
    charset = string.ascii_letters + string.digits
    n = len(charset)
    return ''.join(charset[random.randrange(n)] for _ in range(length))
