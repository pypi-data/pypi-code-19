""" Elastic Modulus Calculation

"""

from celery import group

from pymatgen.analysis.elasticity.strain import DeformedStructureSet, Strain
from pymatgen.analysis.elasticity.stress import Stress
from pymatgen.analysis.elasticity.elastic import ElasticTensor
from pymatgen.transformations.standard_transformations import DeformStructureTransformation
from pymatgen.alchemy.materials import TransformedStructure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

from mattoolkit.utils.celery import app
from mattoolkit.utils.mongodb import (
    MTKStructure, MTKVaspCalculation, MTKAnalysis
)
from mattoolkit.tasks.vasp import vasp_calculation_task


@app.task()
def elastic_workflow(task):
    """ Automates the calculation of Elastic Constants

    Methodology is detailed in doi:10.1038/sdata.2015.9. Proven to work for many systems

    """
    pass


@app.task()
def elastic_calculation_task(task, **kwargs):
    """Calculates deformations of a material using the conventional cell

    Args:
       task (dict): dictionary that contains key 'structure' with mongodb
            structure_id to calculate.
       kwargs: additional arguments supplied to
            :class:`pymatgen.analysis.elasticity.strain.DeformedStructureSet`
    """
    structure_id = task['structure']
    structure = MTKStructure.get(structure_id)
    conv_structure = SpacegroupAnalyzer(structure).get_conventional_standard_structure()
    conv_structure_id = MTKStructure.add(conv_structure, metadata={
        'structure': structure_id,
        'notes': 'conventional structure representation',
        'workflow': 'elastic'
    })

    new_tasks = []
    for deformation in DeformedStructureSet(conv_structure, **kwargs).deformations:
        # using transformed structure instead of
        # `apply_transformation` to have history of each deformation
        deformed_structure_id = MTKStructure.add(
            TransformedStructure(conv_structure, [DeformStructureTransformation(deformation)]),
            metadata={
                'strain': Strain.from_deformation(deformation).tolist(),
                'structure': conv_structure_id,
                'workflow': 'elastic'
            })
        new_tasks.append(vasp_calculation_task.s({
            'structure': deformed_structure_id
        }, mode='relax', user_incar_settings={'ISIF': 2, 'EDIFF': 1E-6, 'ALGO': 'N', 'ENCUT': 700}))

    (group(new_tasks) | elastic_analysis_task.s(initial_structure_id=conv_structure_id)).apply_async()


@app.task
def elastic_analysis_task(tasks, initial_structure_id):
    """ Calculates Elastic Constants from several vasp calculations

    Should *only* be called after an elastic_calculation_task

    Args:
        tasks (list): results from multiple celery vasp_calculation_task
            containing key 'structure' and 'calculation'
        initial_structure_id (ObjectId): structure id of structure being testing for elastic calculations
    """
    stresses = []
    strains = []

    for task in tasks:
        calculation = MTKVaspCalculation.get(task['calculation'])
        # Since elastic_calculation_task does a relaxation it creates a new structure
        # We want the original deformed structure with deformation information
        structure = MTKStructure.get(calculation['metadata']['from_structure'])

        if not isinstance(structure, TransformedStructure):
            raise TypeError('Structure must be transformed structure for elastic analysis')

        strains.append(Strain.from_deformation(structure.history[0]['init_args']['deformation']))
        stresses.append(Stress(calculation['vasprun']['output']['ionic_steps'][-1]['stress']))

    elastic = ElasticTensor.from_strain_stress_list(strains, stresses)
    elastic *= -0.1  # Convert units/sign convention of vasp stress tensor

    initial_structure = MTKStructure.get(initial_structure_id)

    analysis_id = MTKAnalysis.add({
        'analysis': 'Elastic Constants',
        'formula': initial_structure.formula,
        'structures': [task['structure'] for task in tasks],
        'calculations': [task['calculation'] for task in tasks],
        'strains': [strain.tolist() for strain in strains],
        'stresses': [stress.tolist() for stress in stresses],
        'elastic_tensor': elastic.tolist(),
        'voigt': elastic.voigt.tolist(),
        'anisotropy': elastic.universal_anisotropy,
        'poison': elastic.homogeneous_poisson,
        'K_Voigt': elastic.k_voigt, 'G_Voigt': elastic.g_voigt,
        'K_Reuss': elastic.k_reuss, 'G_Reuss': elastic.g_reuss,
        'K_Voigt_Reuss_Hill': elastic.k_vrh, 'G_Voigt_Reuss_Hill': elastic.g_vrh,
        'thermal': thermal_analayis(initial_structure, elastic)
    })

    return {
        'analysis': analysis_id
    }


def thermal_analayis(structure, elastic_tensor):
    """ Thermal Analysis of material from elastic constants

    Reference: `mpworks/firetasks/elastic_tasks.py`
    """
    nsites = structure.num_sites
    volume = structure.volume
    natoms = structure.composition.num_atoms
    weight = structure.composition.weight
    num_density = 1e30 * nsites / volume
    mass_density = 1.6605e3 * nsites * volume * weight / (natoms * volume)
    tot_mass = sum([e.atomic_mass for e in structure.species])
    avg_mass = 1.6605e-27 * tot_mass / natoms

    y_mod = 9e9 * elastic_tensor.k_vrh * elastic_tensor.g_vrh / (3. * elastic_tensor.k_vrh * elastic_tensor.g_vrh)
    trans_v = 1e9 * elastic_tensor.k_vrh / mass_density**0.5
    long_v = 1e9 * elastic_tensor.k_vrh + 4./3. * elastic_tensor.g_vrh / mass_density**0.5
    clarke = 0.87 * 1.3806e-23 * avg_mass**(-2./3.) * mass_density**(1./6.) * y_mod**0.5
    cahill = 1.3806e-23 / 2.48 * num_density**(2./3.) * long_v + 2 * trans_v
    snyder_ac = 0.38483 * avg_mass * (long_v + 2./3.*trans_v)**3. / (300. * num_density**(-2./3.) * nsites**(1./3.))
    snyder_opt = 1.66914e-23 * (long_v + 2./3.*trans_v) / num_density**(-2./3.) * (1 - nsites**(-1./3.))
    snyder_total = snyder_ac + snyder_opt
    debye = 2.489e-11 * avg_mass**(-1./3.) * mass_density**(-1./6.) * y_mod**0.5

    return {
        "num_density": num_density,
        "mass_density": mass_density,
        "avg_mass": avg_mass,
        "num_atom_per_unit_formula": natoms,
        "youngs_modulus": y_mod,
        "trans_velocity": trans_v,
        "long_velocity": long_v,
        "clarke": clarke,
        "cahill": cahill,
        "snyder_acou_300K": snyder_ac,
        "snyder_opt": snyder_opt,
        "snyder_total": snyder_total,
        "debye": debye
    }
