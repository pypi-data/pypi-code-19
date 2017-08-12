# import the BOXMOX module
import boxmox

# make a new run, based on an example supplied by the BOXMOX installation
exp = boxmox.ExperimentFromExample('chamber_experiment')

# inspect namelist
print(exp.namelist)

# change some values
exp.namelist['tend'] = 3600.0 * 12.0 # 12 hours
exp.namelist['dt']   = 600.0         # 10 minutes

# inspect initial conditions
print(exp.input['InitialConditions'])

# change some values
exp.input['InitialConditions']['NO2'] = 0.020 # 20 ppbv NO2

# make a simulation
exp.run()

# load reference to matplotlib pyplot state machine
import matplotlib.pyplot as plt

# plot some concentrations
exp.plot(['O3', 'NO2', 'HNO3'])
plt.show()
