from marshmallow import fields, validate, ValidationError
from marshmallow.decorators import validates_schema, post_load

from ..base import BaseSchema
from ..fields import PolyField


class KpointsGridSchema(BaseSchema):
    CENTERING = {'gamma', 'monkhorst'}

    mode = fields.String(required=True, validate=validate.Equal('grid'))
    centering = fields.String(required=True, validate=validate.OneOf(CENTERING))
    grid = fields.List(fields.Integer, validate=validate.Length(equal=3))
    offset = fields.List(fields.Integer)


class KpointsPathsSchema(BaseSchema):
    kpoint = fields.List(fields.Float, validate=validate.Length(equal=3), required=True)
    label = fields.String(required=True)


class KpointsLineSchema(BaseSchema):
    mode = fields.String(required=True, validate=validate.Equal('line'))
    paths = fields.List(fields.Nested(KpointsPathsSchema, required=True, many=True, validate=validate.Length(min=2)))


class KpointsAutomaticSchema(BaseSchema):
    mode = fields.String(required=True, validate=validate.Equal('automatic'))
    grid_density = fields.Integer()
    reciprocal_density = fields.Integer()
    length = fields.Integer()
    line_density = fields.Integer()

    @validates_schema
    def validate_schema(self, data):
        if len(data.keys() - {'mode'}) != 1:
            raise ValidationError('only one key allowed for automatic mode keys: %s' % ', '.join(data.keys() - {'mode'} or ['none specified']), '_schema')


def kpoints_property_schema_serialization_disambiguation(base_object, obj):
    type_to_schema = {
        'grid': KpointsGridSchema,
        'line': KpointsLineSchema,
        'automatic': KpointsAutomaticSchema
    }
    try:
        return type_to_schema[obj.mode]()
    except KeyError:
        pass
    raise TypeError("Could not detect type did you specify a mode?")


def kpoints_property_schema_deserialization_disambiguation(object_dict, data):
    type_to_schema = {
        'grid': KpointsGridSchema,
        'line': KpointsLineSchema,
        'automatic': KpointsAutomaticSchema
    }
    try:
        return type_to_schema[object_dict['mode']]()
    except KeyError:
        pass
    raise TypeError("Could not detect type did you specify a mode?")


class PotcarElementSchema(BaseSchema):
    element = fields.String(required=True)
    extension = fields.String(required=True)


class PotcarSchema(BaseSchema):
    FUNCTIONALS = {"PBE", "LDA", "PW91", "LDA_US"}

    functional = fields.String(validate=validate.OneOf(FUNCTIONALS))
    symbols = fields.Nested(PotcarElementSchema, many=True)


class VaspInputSchema(BaseSchema):
    TEMPLATES = {'none', 'static', 'relax', 'nonscf'}

    template = fields.String(validate=validate.OneOf(TEMPLATES))
    incar = fields.Dict()
    kpoints = PolyField(
        serialization_schema_selector=kpoints_property_schema_serialization_disambiguation,
        deserialization_schema_selector=kpoints_property_schema_deserialization_disambiguation,
    )
    potcar = fields.Nested(PotcarSchema)

    @validates_schema
    def validate_schema(self, data):
        if 'template' not in data and not data.keys() == {'incar', 'kpoints', 'potcar'}:
            raise ValidationError('incar, kpoints, and potcar required if no template supplied', '_schema')
        elif 'template' not in data and data['kpoints']['mode'] == 'automatic':
            raise ValidationError('cannot have automatically generated kpoints without template', '_schema')
