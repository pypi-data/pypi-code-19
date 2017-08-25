from pyconrad import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation

jvm = PyConrad()
jvm.setup()
jvm.add_import('edu.stanford.rsl.conrad.phantom')

phantom = PyGrid.from_grid(jvm['NumericalSheppLogan3D'](200,200,200).getNumericalSheppLoganPhantom())

fig = plt.figure()

ims = []
for i in range(phantom.shape[0]):
    im = plt.imshow(phantom[i], animated=True)
    ims.append([im])

ani = animation.ArtistAnimation(fig, ims, interval=25, blit=True,
                                repeat_delay=0)
# ani.save('dynamic_images.mp4')
plt.show()
