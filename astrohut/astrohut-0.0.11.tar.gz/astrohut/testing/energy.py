import numpy as np
import astrohut as ah
import matplotlib.pyplot as plt

sim = ah.Simulation(np.random.random((100, 6)), tau = 0.0, epsilon = 1e-1)

sim.start(1e3, save_to_array_every = 10)

fig, ax = plt.subplots()

ax.plot(sim.getEnergies())
ax.set_xlabel("Saved points")
ax.set_ylabel(r"Energy ($\frac{GmM}{r} + \frac{1}{2}mv^2$)")

fig.tight_layout()
plt.show()
