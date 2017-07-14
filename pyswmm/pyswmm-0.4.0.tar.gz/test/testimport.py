import pyswmm
#pyswmm.lib.use("_____REAL___swmm5")


from pyswmm import Simulation


sim = Simulation('OutputTestModel522_SHORT.inp')
print sim.engine_version
print sim.engine_version < sim.engine_version
