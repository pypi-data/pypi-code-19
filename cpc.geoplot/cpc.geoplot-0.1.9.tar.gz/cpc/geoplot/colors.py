
# --------------------------------------------------------------------------------------------------
# tmean terciles
#
# List of RGB tuples representing below, near, and above normal tmean values
tmean_terciles = [
    # Below normal
    (0.01, 0.31, 0.48),
    (0.02, 0.44, 0.69),
    (0.21, 0.56, 0.75),
    (0.45, 0.66, 0.81),
    (0.65, 0.74, 0.86),
    (0.82, 0.82, 0.90),
    (0.95, 0.93, 0.96),
    # Near normal
    (0.75, 0.75, 0.75),
    # Above normal
    (1.00, 0.94, 0.85),
    (0.99, 0.83, 0.62),
    (0.99, 0.73, 0.52),
    (0.99, 0.55, 0.35),
    (0.94, 0.40, 0.28),
    (0.84, 0.19, 0.12),
    (0.60, 0.00, 0.00)
]

# --------------------------------------------------------------------------------------------------
# precip terciles
#
# List of RGB tuples representing below, near, and above median precip values
precip_terciles = [
    # Below median
    (0.26, 0.13, 0.01),
    (0.36, 0.19, 0.02),
    (0.45, 0.25, 0.02),
    (0.63, 0.39, 0.12),
    (0.74, 0.56, 0.33),
    (0.85, 0.73, 0.55),
    (0.96, 0.90, 0.76),
    # Near median
    (0.75, 0.75, 0.75),
    # Above median
    (0.93, 0.97, 0.98),
    (0.80, 0.93, 0.90),
    (0.60, 0.85, 0.79),
    (0.40, 0.76, 0.64),
    (0.25, 0.68, 0.46),
    (0.14, 0.55, 0.27),
    (0.00, 0.35, 0.14)
]

# --------------------------------------------------------------------------------------------------
# tmean two-category
#
# List of RGB tuples representing below and above normal tmean values
tmean_two_cat = [
    # Below normal
    (0.02, 0.35, 0.55),
    (0.17, 0.55, 0.75),
    (0.45, 0.66, 0.81),
    (0.74, 0.79, 0.88),
    (0.95, 0.93, 0.96),
    # Middle of color bar (between -50% and 50%, not plotted by will still be in the colorbar)
    (0.75, 0.75, 0.75),
    # Above normal
    (1.00, 1.00, 0.70),
    (1.00, 0.80, 0.36),
    (0.99, 0.55, 0.24),
    (0.94, 0.23, 0.13),
    (0.74, 0.00, 0.15),
]

# --------------------------------------------------------------------------------------------------
# Define a dict with all the colors
#
# I realized when I wanted to add colors for 500hgt that it won't work because variables can't
# begin with a number. So instead I'm putting new variables as a key in the colors dict.
colors = {}
colors['tmean_terciles'] = tmean_terciles
colors['precip_terciles'] = precip_terciles
colors['tmean_two_cat'] = tmean_two_cat
colors['500hgt_two_cat'] = colors['tmean_two_cat']
colors['500hgt_terciles'] = [
    # Below normal
    (0.01, 0.31, 0.48),
    (0.02, 0.44, 0.69),
    (0.21, 0.56, 0.75),
    (0.45, 0.66, 0.81),
    (0.65, 0.74, 0.86),
    (0.82, 0.82, 0.90),
    (0.95, 0.93, 0.96),
    # Near normal
    (0.75, 0.75, 0.75),
    # Above normal
    (1.00, 0.94, 0.85),
    (0.99, 0.83, 0.62),
    (0.99, 0.73, 0.52),
    (0.99, 0.55, 0.35),
    (0.94, 0.40, 0.28),
    (0.84, 0.19, 0.12),
    (0.60, 0.00, 0.00)
]
colors['precip_two_cat'] = [
    # Below normal
    (0.60, 0.20, 0.016),
    (0.85, 0.37, 0.05),
    (1.00, 0.60, 0.16),
    (1.00, 0.85, 0.56),
    (1.00, 1.00, 0.83),
    # Near normal
    (0.75, 0.75, 0.75),
    # Above normal
    (0.93, 0.97, 0.98),
    (0.70, 0.89, 0.89),
    (0.40, 0.76, 0.64),
    (0.17, 0.64, 0.37),
    (0.00, 0.43, 0.17)
]
