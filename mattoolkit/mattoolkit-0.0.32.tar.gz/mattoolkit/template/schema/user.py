from marshmallow import Schema, fields, validate

from .base import GenericSchema


class UserSpecSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True)
    email = fields.String(required=True)
    first_name = fields.String()
    last_name = fields.String()
    roles = fields.List(fields.String())


class UserSchema(GenericSchema):
    spec = fields.Nested(UserSpecSchema, required=True)
