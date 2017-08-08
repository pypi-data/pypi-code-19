from pymatgen.transformations.site_transformations import (
    InsertSitesTransformation, ReplaceSiteSpeciesTransformation, RemoveSitesTransformation,
    TranslateSitesTransformation, PartialRemoveSitesTransformation, AddSitePropertyTransformation
)
from pymatgen.transformations.standard_transformations import (
    RotationTransformation, OxidationStateDecorationTransformation, AutoOxiStateDecorationTransformation,
    OxidationStateRemovalTransformation, SubstitutionTransformation,
    RemoveSpeciesTransformation, PartialRemoveSpecieTransformation, OrderDisorderedStructureTransformation,
    DeformStructureTransformation,
)
from pymatgen.transformations.defect_transformations import (
    VacancyTransformation, SubstitutionDefectTransformation, AntisiteDefectTransformation,
    InterstitialTransformation
)

from .additions import ElasticTransformation, ConventionalCellTransformation, DuplicateTransformation, SupercellTransformation, PerturbStructureTransformation, DisplacementTransformation, PrimitiveCellTransformation


transformation_map = {
    'InsertSitesTransformation': InsertSitesTransformation,
    'ReplaceSiteSpeciesTransformation': ReplaceSiteSpeciesTransformation,
    'RemoveSitesTransformation': RemoveSitesTransformation,
    'TranslateSitesTransformation': TranslateSitesTransformation,
    'PartialRemoveSitesTransformation': PartialRemoveSitesTransformation,
    'AddSitePropertyTransformation': AddSitePropertyTransformation,
    'RotationTransformation': RotationTransformation,
    'OxidationStateDecorationTransformation': OxidationStateDecorationTransformation,
    'AutoOxiStateDecorationTransformation': AutoOxiStateDecorationTransformation,
    'OxidationStateRemovalTransformation': OxidationStateRemovalTransformation,
    'SubstitutionTransformation': SubstitutionTransformation,
    'RemoveSpeciesTransformation': RemoveSpeciesTransformation,
    'PartialRemoveSpecieTransformation': PartialRemoveSpecieTransformation,
    'OrderDisorderedStructureTransformation': OrderDisorderedStructureTransformation,
    'PrimitiveCellTransformation': PrimitiveCellTransformation,
    'DeformStructureTransformation': DeformStructureTransformation,
    'VacancyTransformation': VacancyTransformation,
    'SubstitutionDefectTransformation': SubstitutionDefectTransformation,
    'AntisiteDefectTransformation': AntisiteDefectTransformation,
    'InterstitialTransformation': InterstitialTransformation,
    'ElasticTransformation': ElasticTransformation,
    'ConventionalCellTransformation': ConventionalCellTransformation,
    'DuplicateTransformation': DuplicateTransformation,
    'SupercellTransformation': SupercellTransformation,
    'PerturbStructureTransformation': PerturbStructureTransformation,
    'DisplacementTransformation': DisplacementTransformation
}


def apply_transformations(structure, transformations):
    def get_ranked_list(limit):
        if limit < 0:
            ranked_list = True
        elif limit == 0:
            ranked_list = False
        else:
            ranked_list = limit
        return ranked_list

    input_structures = [structure]
    for transformation in transformations:
        output_structures = []
        t = transformation_map[transformation['type']](**transformation.get('arguments', {}))
        for s in input_structures:
            result = t.apply_transformation(s, return_ranked_list=get_ranked_list(transformation.get('limit', 0)))
            if t.is_one_to_many:
                for r in result:
                    output_structures.append(r['structure'])
            else:
                output_structures.append(result['structure'])
        input_structures = output_structures
    return output_structures
