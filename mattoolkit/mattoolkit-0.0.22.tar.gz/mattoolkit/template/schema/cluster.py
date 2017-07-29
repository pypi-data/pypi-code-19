from marshmallow import Schema, fields, validate

from .base import GenericSchema


class ClusterSSHSchema(Schema):
    username = fields.String(required=True)
    hostname = fields.String(required=True)
    port = fields.Integer(required=True)


class ClusterModulesSchema(Schema):
    program = fields.String(required=True)
    module = fields.String(required=True)
    command = fields.String(required=True)


class ClusterSpecSchema(Schema):
    ssh = fields.Nested(ClusterSSHSchema)
    scratch_directory = fields.String()
    modules = fields.Nested(ClusterModulesSchema, many=True)


class ClusterSchema(GenericSchema):
    spec = fields.Nested(ClusterSpecSchema)
