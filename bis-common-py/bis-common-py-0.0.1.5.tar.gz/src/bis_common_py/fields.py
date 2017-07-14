# coding: utf-8
from rest_framework.fields import SerializerMethodField


class WritableSerializerMethodField(SerializerMethodField):
    @property
    def read_only(self):
        return False

    @read_only.setter
    def read_only(self, value):
        pass