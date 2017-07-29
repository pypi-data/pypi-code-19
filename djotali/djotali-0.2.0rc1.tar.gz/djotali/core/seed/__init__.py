# coding: utf-8

from faker.providers import BaseProvider
import factory


class SenegalesePhoneNumberProvider(BaseProvider):
    __provider__ = "senegal_phone_number"
    __lang__ = "fr_FR"

    _prefixes = [70, 76, 77, 78, ]

    @classmethod
    def senegal_phone_number(cls):
        area_code = '+221' if cls.random_int(max=1) == 1 else ''
        prefix = cls.random_element(cls._prefixes)
        part_1 = '%03d' % cls.random_int(max=999)
        part_2 = '%02d' % cls.random_int(max=99)
        part_3 = '%02d' % cls.random_int(max=99)
        return '{}{}{}{}{}'.format(area_code, prefix, part_1, part_2, part_3)


factory.Faker.add_provider(SenegalesePhoneNumberProvider)
