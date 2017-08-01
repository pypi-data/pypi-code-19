import random
import string

__CHARS = string.ascii_letters + string.digits


def generate_random_string(length=10):
    return ''.join(random.choice(__CHARS) for _ in range(length))