class RequestBodyBuilder:

    @staticmethod
    def build_send_yo_body(username, api_token, text=None, link=None, coordinate=None):
        body = {
            "username": username,
            "api_token": api_token,
            "text": text,
            "link": link
        }

        if coordinate is not None:
            body["location"] = "{latitude},{longitude}".format(latitude=coordinate.latitude, longitude=coordinate.longitude)

        return body

    @staticmethod
    def build_send_yo_to_all_subscribers_body(api_token, link=None):
        return {"link": link, "api_token": api_token}

    @staticmethod
    def build_account_creation_body(username, api_token, password=None, callback_url=None, email=None, description=None, needs_location=False, welcome_link=None):
        return {
            "username": username,
            "api_token": api_token,
            "password": password,
            "callback_url": callback_url,
            "email": email,
            "description": description,
            "needs_location": needs_location,
            "welcome_link": welcome_link
        }


class RequestQueryParametersBuilder:

    @staticmethod
    def build_username_exists_query_parameters(username, api_token):
        return {
            "username": username,
            "api_token": api_token
        }