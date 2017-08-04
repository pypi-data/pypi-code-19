from pymatgen.analysis.elasticity.strain import DeformedStructureSet, Strain
from pymatgen.transformations.transformation_abc import AbstractTransformation
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from pymatgen.transformations.standard_transformations import (
    SupercellTransformation as _SupercellTransformation,
    PerturbStructureTransformation as _PerturbStructureTransformation
)


class ElasticTransformation(AbstractTransformation):
    """ Generates Elastic Deformations of given structure

    """
    def __init__(self, max_normal=0.02, max_shear=0.05, num_normal=4, num_shear=4):
        self.max_normal = max_normal
        self.max_shear = max_shear
        self.num_normal = num_normal
        self.num_shear = num_shear

    def apply_transformation(self, structure, return_ranked_list=None):
        deformation_set = DeformedStructureSet(
            structure,
            nd=self.max_normal, ns=self.max_shear,
            num_norm=self.num_normal, num_shear=self.num_shear)
        return [{'structure': s} for s in deformation_set.def_structs]

    def __str__(self):
        return f"Elastic Transformation:"

    @property
    def inverse(self):
        return None

    @property
    def is_one_to_many(self):
        return True


class DuplicateTransformation(AbstractTransformation):
    """ Generates Duplicates of a given structrue

    """
    def __init__(self, duplicates=1):
        self.duplicates = duplicates

    def apply_transformation(self, structure, return_ranked_list=None):
        structures = []
        for i in range(self.duplicates):
            structures.append({'structure': structure.copy()})
        return structures

    @property
    def inverse(self):
        return None

    @property
    def is_one_to_many(self):
        return True

class SupercellTransformation(_SupercellTransformation):
    def apply_transformation(self, structure, return_ranked_list=None):
        return {'structure': structure * self.scaling_matrix}

    @property
    def inverse(self):
        raise NotImplementedError()

    @property
    def is_one_to_many(self):
        return False


class PerturbStructureTransformation(_PerturbStructureTransformation):
    def apply_transformation(self, structure, return_ranked_list=None):
        s = structure.copy()
        s.perturb(self.amplitude)
        return {'structure': s}


class ConventionalCellTransformation(AbstractTransformation):
    """ Generates Conventional Unit cell of structure

    """
    def __init__(self, precision=1e-3, angle_tolerance=5):
        self.precision = precision
        self.angle_tolerance = angle_tolerance

    def apply_transformation(self, structure, return_ranked_list=None):
        sga = SpacegroupAnalyzer(structure, self.precision, self.angle_tolerance)
        return {'structure': sga.get_conventional_standard_structure()}

    def __str__(self):
        return "Conventional cell transformation"

    def __repr__(self):
        return self.__str__()


    @property
    def inverse(self):
        return None

    @property
    def is_one_to_many(self):
        return False
