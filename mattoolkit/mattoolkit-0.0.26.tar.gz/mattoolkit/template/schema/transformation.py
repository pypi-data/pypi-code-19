from marshmallow import Schema, fields, validate

from .base import GenericSchema


class TransformationCalculationStructureSelectorSchema(Schema):
    TYPES = ['Calculation', 'Structure']

    type = fields.String(required=True, validate=validate.OneOf(TYPES))
    labels = fields.List(fields.String)


class TransformationStructureSchema(Schema):
    selector = fields.Nested(TransformationCalculationStructureSelectorSchema)


class SingleTransformationSchema(Schema):
    TYPES = [
        # Site Transformations
        'InsertSitesTransformation', # Substitues sites with species and place at coords
        'ReplaceSiteSpeciesTransformation', # Substitutes sites with species.
        'RemoveSitesTransformation', # Remove certain sites in a structure.
        'TranslateSitesTransformation', # Translate a set of sites by vector.
        'PartialRemoveSitesTransformation', # Remove fraction of specie from a structure.
        'AddSitePropertyTransformation', # Add site properties to a given structure.
        # Standard Transformations
        'RotationTransformation', # Apply rotation to structure
        'OxidationStateDecorationTransformation', # Decorate structure with oxidation state
        'AutoOxiStateDecorationTransformation', # Automatic Oxidation using bond valenca approach
        'OxidationStateRemovalTransformation', # Remove Oxidation state from structure
        'SupercellTransformation', # supercell scaling to apply
        'SubstitutionTransformation', # Substitute one species for another
        'RemoveSpeciesTransformation', # Remove all occurences of some species from a structure
        'PartialRemoveSpecieTransformation', # Remove fraction of specie from a structure
        'OrderDisorderedStructureTransformation', # Order a disordered structure.
        'PrimitiveCellTransformation', # Finds the primitive cell of the input structure.
        'PerturbStructureTransformation', # Perturb structure by a specified distance
        'DeformStructureTransformation', # Deform structure with deformation gradient
        # Defect Transformations
        'VacancyTransformation', # Generates vacancy structures
        'SubstitutionDefectTransformation', # Generate substitutional defects
        'AntisiteDefectTransformation', # Generate antisite defect structures
        'InterstitialTransformation', # Generates interstitial structures
        # Not including (advanced transformations yet)
    ]

    type = fields.String(required=True, validate=validate.OneOf(TYPES))
    limit = fields.Integer() # Number of structures to return (0 False, negative True)
    arguments = fields.Dict()


class CalculationSpecSchema(Schema):
    structure = fields.Nested(TransformationStructureSchema, required=True)
    transformations = fields.Nested(SingleTransformationSchema, many=True, required=True)


class TransformationSchema(GenericSchema):
    spec = fields.Nested(CalculationSpecSchema, required=True)
