from marshmallow import Schema, fields, validate, ValidationError
from marshmallow.decorators import validates_schema


class BaseSchema(Schema):
    def __init__(self, strict=True, **kwargs):
        super(Schema, self).__init__(strict=strict, **kwargs)

    @validates_schema(pass_original=True, pass_many=False, skip_on_field_errors=True)
    def check_unknown_fields(self, data, original_data):
        def check_unknown(original_data_single):
            unknown = set(original_data_single) - set(self.fields.keys())
            if unknown:
                raise ValidationError('Unknown field', unknown)

        if isinstance(original_data, list):
            for original_data_single in original_data:
                check_unknown(original_data_single)
        else:
            check_unknown(original_data)


class MetadataSchema(Schema):
    name = fields.String()
    username = fields.String()
    labels = fields.List(fields.String())

class GenericSchema(Schema):
    VERSIONS = ['v1']
    KINDS = ['User', 'Cluster', 'Structure', 'Calculation']

    version = fields.String(required=True, validate=validate.OneOf(VERSIONS))
    kind = fields.String(required=True, validate=validate.OneOf(KINDS))
    metadata = fields.Nested(MetadataSchema)
