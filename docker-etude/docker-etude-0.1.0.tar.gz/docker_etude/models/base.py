"""
Common model behavior.

"""
from abc import ABC, abstractclassmethod, abstractmethod
from collections import OrderedDict


class Model(ABC):

    def to_safe_dict(self):
        """
        Build a null-safed dictionary.

        Validation in docker-compose will fail on null values in some cases.

        """
        dct = OrderedDict()
        for key, value in self.to_dict().items():
            if value:
                dct[key] = value

        if not dct:
            return None

        return dct

    @abstractmethod
    def to_dict(self):
        """
        Convert model to a Python (ordered) dictionary.

        """
        pass

    @abstractclassmethod
    def from_dict(cls, dct):
        """
        Convert Python dictionary to model instance.

        """
        pass
