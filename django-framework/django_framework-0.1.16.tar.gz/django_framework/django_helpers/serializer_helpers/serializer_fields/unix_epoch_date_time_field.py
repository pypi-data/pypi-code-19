from rest_framework import serializers

import arrow

class UnixEpochDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if value == None:
            response = None
        else:
            response = arrow.get(value).timestamp
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = arrow.get(data).datetime
        return response


    