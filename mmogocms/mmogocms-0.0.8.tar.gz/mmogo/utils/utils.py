import random
import hashlib
import uuid
import string


def generate_random_number(length, valid_characters='0123456789'):
    key = ''
    for i in range(length):
        key = '%s%s' % (key, random.choice(valid_characters))
    return key


def generate_random_key(length, valid_characters='abcdefghijklmnopqrstuvwxyz0123456789'):
    key = ''
    for i in range(length):
        key = '%s%s' % (key, random.choice(valid_characters))
    return key


def create_hash(length):
    # uuid is used to generate a random number
    data = uuid.uuid4().hex
    h = hashlib.new(length)
    h.update(data)
    return h.hexdigest()


def generate_uuid():
    data = uuid.uuid4().hex
    return data


def id_generator(size=9, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
