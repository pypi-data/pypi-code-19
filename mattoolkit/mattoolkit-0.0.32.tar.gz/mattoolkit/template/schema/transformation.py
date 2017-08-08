from marshmallow import Schema, fields, validate

from .base import GenericSchema
from ...jobs.transformation import transformation_map


class TransformationCalculationStructureSelectorSchema(Schema):
    TYPES = ['Calculation', 'Structure']

    type = fields.String(required=True, validate=validate.OneOf(TYPES))
    labels = fields.List(fields.String)


class TransformationStructureSchema(Schema):
    selector = fields.Nested(TransformationCalculationStructureSelectorSchema)


class SingleTransformationSchema(Schema):
    TYPES = transformation_map.keys()

    type = fields.String(required=True, validate=validate.OneOf(TYPES))
    limit = fields.Integer() # Number of structures to return (0 False, negative True)
    arguments = fields.Dict()


class CalculationSpecSchema(Schema):
    structure = fields.Nested(TransformationStructureSchema, required=True)
    transformations = fields.Nested(SingleTransformationSchema, many=True, required=True)


class TransformationSchema(GenericSchema):
    spec = fields.Nested(CalculationSpecSchema, required=True)
