import unittest

from jabstract import jabstract


class TestJabstract(unittest.TestCase):
    def test_jabstract_only_overrides_provided(self):
        api_response = jabstract({
            "client": {
                "name": "John doe",
                "email": "johndoe@example.org"
            },
            "status": "received"
        })

        response = api_response(
            client=dict(
                name="Baboon v2.0"
            )
        )

        self.assertEqual(response, {
            "client": {
                "name": "Baboon v2.0",
                "email": "johndoe@example.org"
            },
            "status": "received"
        })


