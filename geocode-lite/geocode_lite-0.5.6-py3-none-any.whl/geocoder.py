import googlemaps

__all__ = ['Geocoder', 'get_lat_lng']


class Geocoder(object):
    def __init__(self, api_key):
        self._client_id = 'gme-corelogicsolutions'
        self._channel = 'geocode-lite'
        self._api_key = api_key

    def get_response(self, address):
        client = googlemaps.Client(client_id=self._client_id, client_secret=self._api_key, channel=self._channel)
        return client.geocode(address)


def get_lat_lng(response):
    lat = response[0]['geometry']['location']['lat']
    lng = response[0]['geometry']['location']['lng']
    return lat, lng



