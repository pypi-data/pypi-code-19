from rest_framework import serializers


from django_framework.django_helpers.serializer_helpers import BaseSerializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import register_serializer
from django_framework.django_helpers.serializer_helpers.serialize_registry import get_serializer


from django_framework.django_helpers.model_helpers.model_registry import get_model

from django_framework.django_helpers.serializer_helpers.serializer_fields import UnixEpochDateTimeField

import json

class JobSerializer(BaseSerializer):
    run_at = UnixEpochDateTimeField(required=False)
    response_at = UnixEpochDateTimeField(required=False)
    completed_at = UnixEpochDateTimeField(required=False)

    status_alt = serializers.SerializerMethodField("_status_alt")
    
    def _status_alt(self, obj):
        response = self.Meta.model.get_field_choice(field_name="status",
                                                 original_choice=obj.status,
                                                 alt=True)
        return response
    
    
    
    class Meta:
        
        model = get_model(model_name="Job")
        fields = BaseSerializer.Meta.fields + ["model_name","model_uuid","model_id",
                                               "command","action",
                                               "intial_payload",
                                               "status","status_alt",
                                               "response_payload",
                                               "error_notes",
                                               "job_timeout",
                                               "run_at","response_at","completed_at",
                                               "job_type"
                                               ]
        read_only_fields = BaseSerializer.Meta.read_only_fields
        hidden_fields = []


register_serializer(JobSerializer, version= 'default')
