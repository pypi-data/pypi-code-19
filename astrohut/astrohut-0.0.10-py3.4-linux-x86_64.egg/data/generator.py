import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt

G = 1
m = 1

pos = np.random.normal(size=(100, 2))
speeds = ah.generateSpeeds(pos, G, m)

system = ah.createArray(pos, speeds)

sim = ah.Simulation(system, tau = 1.0, epsilon = 1e-5)

# nInstants = int(sim.calcRelaxationTime()/sim.dt)
nInstants = 10000

sim.start(nInstants, save_to_array_every = nInstants//100, save_to_file_every = nInstants)
ani = sim.makeAnimation()

plt.show()

plt.plot(sim.getEnergies())
plt.show()
