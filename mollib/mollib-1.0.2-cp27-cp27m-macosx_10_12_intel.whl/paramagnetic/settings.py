#: Number of angstroms to exclude points in a grid if they are within this
#: distance of a molecule atom.
exclusion_cutoff = 3.0

#: Number of Angstroms for the box's dimension
box_max_length = 20

#: Number of Angstroms per point in box
box_density = 0.5

#: These are default dimensions for various molecules or lipid aggregates
shapes = {  # 1. Lipfert, et al. J Phys Chem B 111, 12427 (2007)
          'DPC': {'short': 16.5,   # A
                  'long': 27.5, },  # A
          }
