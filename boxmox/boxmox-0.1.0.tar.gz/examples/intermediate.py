# import the BOXMOX module
import boxmox
import numpy as np

# evaluate differences in run with different NO2 initial conditions
no2_ics  = np.linspace(0.01, 0.3,  20)
c2h4_ics = np.linspace(0.1, 2.000, 20)

X,Y      = np.meshgrid(no2_ics, c2h4_ics)
Z        = np.zeros_like(X)

# make a new experiment, set some values, run, and put the resulting O3 concentration in Z
def run_exp(out, x, y, no2_ic, c2h4_ic):
    exp = boxmox.ExperimentFromExample('chamber_experiment')
    exp.namelist['tend']    = 3600.0 * 1.0  # run time (s)
    exp.namelist['dt']      = 240.0         # time step (s)
    for spec, val in [ ('NO2', no2_ic),
                      ('NO'  , 0.1 * no2_ic),
                      ('C2H4', c2h4_ic) ]:
        exp.input['InitialConditions'][spec] = val
    exp.run()
    out[x, y] = exp.output['Concentrations']['O3'][-1]

# run all the experiments
nul = [ run_exp(Z, x, y, no2, c2h6) for x, no2 in enumerate(no2_ics) for y, c2h6 in enumerate(c2h4_ics) ]

import matplotlib.pyplot as plt

plt.contourf(Z, cmap = plt.cm.jet, vmin=abs(Z).min(), vmax=abs(Z).max(), extent=[c2h4_ics[0], c2h4_ics[-1],no2_ics[0], no2_ics[-1]] )
plt.title('BOXMOX EKMA diagram example')
plt.xlabel(r'C$_2$H$_4$ (ppmv)')
plt.ylabel(r'NO$_x$ (ppmv)')
plt.colorbar(label=r'O$_3$ (ppmv)')
plt.tight_layout()
plt.savefig('ekma.png')

