import numpy as np
from pymatgen.analysis.elasticity.strain import DeformedStructureSet, Strain
from pymatgen.transformations.transformation_abc import AbstractTransformation
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen import Structure

from pymatgen.transformations.standard_transformations import (
    SupercellTransformation as _SupercellTransformation,
    PerturbStructureTransformation as _PerturbStructureTransformation,
    PrimitiveCellTransformation as _PrimitiveCellTransformation
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
        return [structure.copy()] + [{'structure': s} for s in deformation_set.def_structs]

    def __str__(self):
        return f"Elastic Transformation:"

    @property
    def inverse(self):
        return None

    @property
    def is_one_to_many(self):
        return True


class DisplacementTransformation(AbstractTransformation):
    """ Generates unique displacements of a given structure.

    Uses Phonopy to generate these displacements. (maybe one day will be able to avoid)
    """
    def __init__(self, displacement=0.01, supercell=None):
        self.displacement = 0.01 # Angstroms
        self.supercell = supercell or ((1, 0, 0), (0, 1, 0), (0, 0, 1))

    def apply_transformation(self, structure, return_ranked_list=None):
        from phonopy import Phonopy
        from phonopy.structure.atoms import PhonopyAtoms

        sga = SpacegroupAnalyzer(structure)
        primitive = sga.get_primitive_standard_structure()

        symbols = []
        scaled_positions = []
        for atom in structure:
            symbols.append(atom.specie.name)
            scaled_positions.append(atom.frac_coords)
        structure_unitcell = PhonopyAtoms(symbols=symbols, cell=structure.lattice.matrix, scaled_positions=scaled_positions)

        # Generate Primitive matrix from primitive cell (has to be normalized in a special way)
        row_sums = primitive.lattice.matrix.sum(axis=1)
        primitive_matrix = primitive.lattice.matrix / row_sums[:, np.newaxis]

        phonon = Phonopy(structure_unitcell, self.supercell, primitive_matrix=primitive_matrix)
        phonon.generate_displacements(distance=self.displacement)
        supercell_structures = [phonon.get_supercell()]
        supercell_structures += phonon.get_supercells_with_displacements()

        structures = []
        for s in supercell_structures:
            structures.append({'structure': Structure(lattice=s.get_cell(),
                                                      species=s.get_chemical_symbols(),
                                                      coords=s.get_scaled_positions())})
        return structures


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


class PrimitiveCellTransformation(_PrimitiveCellTransformation):
    def apply_transformation(self, structure, return_ranked_list=None):
        return {'structure': structure.get_primitive_structure(tolerance=self.tolerance)}


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
