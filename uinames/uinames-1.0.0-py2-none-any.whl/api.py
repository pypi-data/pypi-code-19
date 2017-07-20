import requests

from models import Person, People


def generate_random_identity():
    """
    A basic function to generate a single, random identity, in the form of a
    Person instance.
    """
    json = _send_raw("https://uinames.com/api/")

    return Person(json)


def generate_random_identities(amount=1, gender=None, region=None,
                               minlen=None, maxlen=None, ext=False):
    """
    A function that returns a People instance, which contains a list of random
    Person instances.

    amount: The number of identities to generate. This should be an integer
        between 1 and 500 (inclusive).
    gender: The gender of the identities generated. This should be one of the
        following string literals: "male" or "female".
    region: The region of origin of the identities generated. The list of valid
        regions can be found in this file
        https://github.com/thm/uinames/blob/master/uinames.com/api/names.json.
        Generally, any lowercase country, spelled correctly will be valid.
    minlen: The minimum combined name and surname length of the identity.
    maxlen: The maximum combined name and surname length of the identity.
    ext: When specified, this will return extra data with each identity,
        including: age, title, phone, birthday, email, password, credit card,
        and a photo.
    """
    params = {
        "amount": amount,
        "gender": gender,
        "region": region,
        "minlen": minlen,
        "maxlen": maxlen
    }

    if ext:
        params["ext"] = ext

    json = _send_raw("https://uinames.com/api/", params=params)

    return People([json]) if amount == 1 else People(json)


def _send_raw(url, params=None):
    """
    A low level function used to make the necessary HTTP requests to access the
    UINames API.
    """
    response = requests.get(url, params=params)
    response.raise_for_status()

    return response.json()


if __name__ == "__main__":
    pass
