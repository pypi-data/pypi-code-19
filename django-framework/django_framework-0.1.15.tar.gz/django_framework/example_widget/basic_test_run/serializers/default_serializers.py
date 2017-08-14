from rest_framework import serializers
import arrow

from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer

from django_framework.django_helpers.serializer_helpers.serializer_fields import ManyToManyIdListField, TripleDesField, UnixEpochDateTimeField
from django_framework.django_helpers.model_helpers.model_registry import get_model
from django.core.exceptions import ValidationError

class BasicTestRunSerializer(BaseSerializer):

    basic_profile_run_fk_field_id = serializers.IntegerField()
    
    basic_profile_run_ids = ManyToManyIdListField(source="basic_profile_run", required=False)
    
    epoch_time_field = UnixEpochDateTimeField(required=False)
    epoch_time_field_alt = serializers.SerializerMethodField(required=False)

    encrypted_text_field = TripleDesField(allow_unencrypt = True, required = False)
    encrypted_text_strict_field = TripleDesField(allow_unencrypt = False, required = False)

    choices_field_alt = serializers.SerializerMethodField()
    
    
    def get_epoch_time_field_alt(self, obj):
        return self._get_time_alt(value = getattr(obj, 'epoch_time_field'))

    def get_choices_field_alt(self, obj):
        response = self._get_code_alt(field_name = 'choices_field', obj = obj)
        return response

    class Meta:
        
        model = get_model(model_name="BasicTestRun")
        fields = BaseSerializer.Meta.fields + [
            "basic_profile_run_fk_field_id",
            "basic_profile_run_ids",
            "normal_text_field", 
            
            "write_once_text_field",
             "read_only_text_field",
            "encrypted_text_field", 
            "encrypted_text_strict_field", 
            "epoch_time_field", "epoch_time_field_alt",
            "choices_field", "choices_field_alt",
        ]
        
        read_only_fields = BaseSerializer.Meta.read_only_fields + ['read_only_text_field']  # not allowed to edit, will not throw error
        hidden_fields = ["hidden_text_field"] # not shown to user
        write_once_fields = ["write_once_text_field"] # can only be set upon creation. not editable after
        


register_serializer(BasicTestRunSerializer, version= 'default')
