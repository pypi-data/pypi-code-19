import numpy as np
from prody.atomic import ATOMIC_FIELDS, AtomGroup
import json


def parse_atlas(atlas_filepath):
    with open(atlas_filepath, "r") as f:
        return parse_atlas_stream(f)


def parse_atlas_stream(atlas_stream):
    atlas_data = json.load(atlas_stream)

    atomgroup = AtomGroup('atoms')
    atoms = atlas_data.get("atoms")
    natoms = len(atoms)

    coordinates = np.zeros((len(atoms), 3), dtype=float)
    atomnames = np.zeros(natoms, dtype=ATOMIC_FIELDS['name'].dtype)
    resnames = np.zeros(natoms, dtype=ATOMIC_FIELDS['resname'].dtype)
    resnums = np.zeros(natoms, dtype=ATOMIC_FIELDS['resnum'].dtype)
    chainids = np.zeros(natoms, dtype=ATOMIC_FIELDS['chain'].dtype)
    hetero = np.zeros(natoms, dtype=bool)
    termini = np.zeros(natoms, dtype=bool)
    altlocs = np.zeros(natoms, dtype=ATOMIC_FIELDS['altloc'].dtype)
    icodes = np.zeros(natoms, dtype=ATOMIC_FIELDS['icode'].dtype)
    serials = np.zeros(natoms, dtype=ATOMIC_FIELDS['serial'].dtype)

    for i, atom in enumerate(atoms):
        coordinates[i, 0] = atom['x']
        coordinates[i, 1] = atom['y']
        coordinates[i, 2] = atom['z']

        atomnames[i] = atom['name']
        resnums[i] = atom['residue']
        chainids[i] = atom['segment']
        resnames[i] = atom.get('residue_name', "")

        serials[i] = i + 1

    atomgroup._setCoords(coordinates)
    atomgroup.setNames(atomnames)
    atomgroup.setResnames(resnames)
    atomgroup.setResnums(resnums)
    atomgroup.setChids(chainids)
    atomgroup.setAltlocs(altlocs)
    atomgroup.setFlags('hetatm', hetero)
    atomgroup.setFlags('pdbter', termini)
    atomgroup.setIcodes(np.char.strip(icodes))
    atomgroup.setSerials(serials)

    return atomgroup
