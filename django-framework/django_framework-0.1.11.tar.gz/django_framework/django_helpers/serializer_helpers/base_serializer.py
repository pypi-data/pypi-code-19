from rest_framework import serializers

from django_framework.django_helpers.model_helpers.model_registry import get_model_name

from serializer_fields import UnixEpochDateTimeField
from serializer_validators import HiddenFieldsValidator, WriteOnceFieldsValidator

import arrow



class BaseSerializer(serializers.ModelSerializer):

    last_updated = UnixEpochDateTimeField(required=False)
    created_at = UnixEpochDateTimeField(required=False)

    last_updated_alt = serializers.SerializerMethodField(required=False)
    created_at_alt = serializers.SerializerMethodField(required=False)
    
    type = serializers.SerializerMethodField() 
    
    def get_last_updated_alt(self, obj):
        return arrow.get(getattr(obj, 'last_updated')).format('YYYY-MM-DD HH:mm:ss')

    def get_created_at_alt(self, obj):
        return arrow.get(getattr(obj, 'created_at')).format('YYYY-MM-DD HH:mm:ss')

#     def to_internal_value(self, data):
#         for key in data.keys():
#             if key[-6:] == "_uuids":
#                 self.change_model_uuids_to_ids(data, key)
#             elif key[-5:] == "_uuid":
#                 try:
#                     model_field_name_base = key[:-5]
#                     field = self.Meta.model._meta.get_field(model_field_name_base)
#                     if field.is_relation:
#                         data[model_field_name_base+"_id"] = self.convert_uuid_to_id(
#                             manager_name=get_model_name(field.remote_field.model),
#                             uuid_string=data[key], field_name=model_field_name_base,
#                         )
#                 except FieldDoesNotExist:
#                     pass
# 
#         return super(BaseSerializer, self).to_internal_value(data)

#     def change_model_uuids_to_ids(self, data, key):
#         try:
#             model_field_name_base = key[:-6]
#             field = self.Meta.model._meta.get_field(
#                 Inflector().pluralize(model_field_name_base)
#             )
#             if field.is_relation:
#                 if isinstance(data[key], dict):
#                     update_value = data[key].get("data", [])
#                 else:
#                     update_value = data[key]
# 
#                 update_value = self.convert_uuids_to_ids(
#                     manager_name=get_model_name(model=field.remote_field.model),
#                     uuid_list=update_value, field_name=model_field_name_base,
#                 )
# 
#                 if isinstance(data[key], dict):
#                     data[key]["data"] = update_value
#                     data[model_field_name_base+"_ids"] = data[key]
#                 else:
#                     data[model_field_name_base+"_ids"] = update_value
#         except FieldDoesNotExist:
#             pass

    def get_type(self, obj):
        model_name = None
        if obj:
            full_name, model_name = get_model_name(model=obj)
        return model_name

    def get_validators(self):
        # we must override this method because setting validators
        # causes Django Rest Framework to not load it's standard
        # validators
        response = super(BaseSerializer, self).get_validators()  # get parent serializers
        hidden_fields = getattr(self.Meta, "hidden_fields", None)
        write_once_fields = getattr(self.Meta, "write_once_fields", None)

        
        additional_validators = []

        # check for hidden fields, if so add HiddenFieldsValidator
        # to class-level validators
        if hidden_fields is not None:
            additional_validators.append(HiddenFieldsValidator(fields=hidden_fields))

        # check for write_once fields, if so add WriteOnceFieldsValidator
        # to class-level validators
        if write_once_fields is not None:
            additional_validators.append(WriteOnceFieldsValidator(fields=write_once_fields))


        # if any additonal validators, add to response
        if additional_validators:
            response += tuple(additional_validators)

        return response

#     def convert_uuids_to_ids(self, manager_name, uuid_list, field_name):
#         Manager = get_manager(manager_name=manager_name)
#         query_params = {"filter": {"uuid__in": uuid_list}}
#         models = Manager.get_by_query(query_params=query_params)
#         id_list = []
#         valid_uuids = {str(m.uuid): m for m in models}
#         for uuid_string in uuid_list:
#             if valid_uuids.get(uuid_string):
#                 id_list.append(valid_uuids[uuid_string].id)
#             else:
#                 error = "Invalid uuid in '{field_name}'"
#                 raise ValueError(error.format(field_name=field_name))
# 
#         return id_list
# 
#     def convert_uuid_to_id(self, manager_name, uuid_string, field_name):
#         return self.convert_uuids_to_ids(
#             manager_name=manager_name, uuid_list=[uuid_string], field_name=field_name
#         )[0]

    def _get_code_alt(self, field_name, obj):
        response = self.Meta.model.get_field_choice(
            field_name=field_name, original_choice=getattr(obj, field_name), alt=True
        )
        return response
    

    @classmethod
    def _get_time_alt(cls, value):
        
        return arrow.get(value).format('YYYY-MM-DD HH:mm:ss')


    class Meta:
        
        fields = [
            "id", "type",
            "uuid",

            "created_at", "created_at_alt", "last_updated", "last_updated_alt",
        ]
        read_only_fields = ["id", "type", "uuid", "last_updated", "created_at"]
        hidden_fields = []

