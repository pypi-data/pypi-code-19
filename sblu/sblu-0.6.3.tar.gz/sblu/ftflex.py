"""FTFlex and flexible piper related code
"""

IGNORED_RESIDUES = {
    "ALA",
    "CYS",
    "GLY",
    "ILE",
    "LEU",
    "PRO",
    "SER",
    "THR",
    "VAL"
}
FARAWAY_CUTOFFS = {
    "ARG": 0.8440,
    'ASN': 0.4704,
    'ASP': 0.6208,
    'GLN': 2.9000,
    'GLU': 0.7181,
    'HIS': 1.9500,
    'LYS': 1.5659,
    'MET': 0.1754,
    'PHE': 0.7210,
    'TRP': 0.6088,
    'TYR': 1.0200
}


def get_segment(chain, resnum, pdb_file):
    resnum = str(resnum).strip()
    with open(pdb_file, "r") as f:
        for l in f:
            c = l[21]
            i = l[22:26].strip()
            if c == chain and i == resnum:
                return l[72:76].strip()
    return None


def process_report(report, energy_cutoff=0.0, population_cutoff=10000):
    all_rotamers = []
    low_energy_populated_rotamers = set()
    with open(report, "r") as f:
        for l in f:
            if l.startswith("after rmsd"):
                break

        for l in f:
            ss = l.split()
            all_rotamers.append(ss[0])
            if float(ss[1]) < energy_cutoff and int(ss[5]) >= population_cutoff:
                low_energy_populated_rotamers.add(ss[0])

    return all_rotamers, low_energy_populated_rotamers


