from marshmallow import Schema, fields, validate

from .base import GenericSchema


class CalculationStructureSelectorSchema(Schema):
    TYPES = ['Calculation', 'Structure']

    type = fields.String(required=True, validate=validate.OneOf(TYPES))
    many = fields.Boolean(required=True)
    labels = fields.List(fields.String)
    ids = fields.List(fields.Integer)


class CalculationStructureSchema(Schema):
    selector = fields.Nested(CalculationStructureSelectorSchema)


class CalculationCalculationSchema(Schema):
    SOFTWARES = ['VASP']

    software = fields.String(required=True, validate=validate.OneOf(SOFTWARES))
    template = fields.String()
    incar = fields.Dict()
    kpoints = fields.Dict()


class CalculationJobSchema(Schema):
    cluster = fields.String(required=True)
    queue = fields.String(required=True)
    cores = fields.Integer(default=1)
    time = fields.String(default='01:00:00', validate=validate.Regexp('\d+:\d+:\d+'))


class CalculationSpecSchema(Schema):
    structure = fields.Nested(CalculationStructureSchema)
    calculation = fields.Nested(CalculationCalculationSchema, required=True)
    job = fields.Nested(CalculationJobSchema, required=True)


class CalculationSchema(GenericSchema):
    spec = fields.Nested(CalculationSpecSchema, required=True)
