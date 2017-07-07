import arrow


from django_framework.django_helpers.manager_helpers.base_manager import BaseManager

from django_framework.django_helpers.manager_helpers import register_manager

from django_framework.django_helpers.model_helpers import get_model

from django_framework.django_helpers.serializer_helpers import get_serializer
from django_framework.helpers.security_helpers import generate_unique_key, md5_hasher

class ProfileManager(BaseManager):
    Model = get_model(model_name = 'Profile')

    @classmethod
    def _relationship_name_format(cls, relationship_name=None, relationship_list=None):
        if relationship_name == 'profile':
            query_key = 'id__in'
        return query_key, relationship_list



    @classmethod
    def set_security_code(cls, profile):
        security_code = generate_unique_key(length = 6, dashes = False, numbers_only = False)
        hashed_security_code = md5_hasher(security_code)
        
        security_code_valid_until = arrow.utcnow().repalce(hours =+ 1).timestamp
        
        serializer = get_serializer(model_name = 'Profile', version = 'admin')
        objs = cls.update(Serializer=serializer, data = {"security_code" : hashed_security_code, "security_code_valid_until" : security_code_valid_until}, model = profile)
        
        return objs, security_code
        
register_manager(ProfileManager)
