from marshmallow import Schema, fields, validate

from .base import GenericSchema


class StructureSpecSchema(Schema):
    FORMATS = ['cif']

    format = fields.String(required=True, validate=validate.OneOf(FORMATS))
    data = fields.String(required=True)


class StructureSchema(GenericSchema):
    spec = fields.Nested(StructureSpecSchema, required=True)
