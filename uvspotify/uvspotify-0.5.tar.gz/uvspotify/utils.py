from nose.tools import *
from uvoauth.utils import OauthServer, FIRST_TOKEN
from sanic.response import json

class SpotifyServer(OauthServer):
    def add_routes(self):
        super().add_routes()

        self.app.add_route(self.token, '/api/token', methods=['POST'])
        self.app.add_route(self.devices, '/v1/me/player/devices')

    async def devices(self, request):
        assert_in(request.headers['Authorization'], 'Bearer ' + FIRST_TOKEN)

        return json({
            "devices": [
                {
                    "id": "hello",
                    "is_active": False,
                    "is_restricted": False,
                    "name": "Kitchen",
                    "type": "speaker",
                    "volume_percent": 100
                },
                {
                    "id": "hello2",
                    "is_active": True,
                    "is_restricted": False,
                    "name": "Living Room",
                    "type": "speaker",
                    "volume_percent": 100
                },
            ]
        })
