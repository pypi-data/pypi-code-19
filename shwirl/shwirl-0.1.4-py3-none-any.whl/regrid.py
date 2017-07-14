import numpy as np
from matplotlib import pyplot as plt
from astropy.io import fits

# Normalize to [0,1]
cube1 = fits.open('result-ngc3256_line_CNhi.image.fits')[0].data[0]
cube2 = fits.open('result-ngc3256_line_CO.image.fits')[0].data[0]


cube2 -= cube2.min()
cube2 /= cube2.max() - cube2.min()

# cube2 -= min(np.nanmin(cube1), np.nanmin(cube2))
# cube2 /= max(np.nanmax(cube1), np.nanmax(cube2)) - min(np.nanmin(cube1), np.nanmin(cube2))

cube1 -= min(np.nanmin(cube1), np.nanmin(cube2))
cube1 /= max(np.nanmax(cube1), np.nanmax(cube2)) - min(np.nanmin(cube1), np.nanmin(cube2))


print ('\tCNhi\t\tCO')
print ('Min\t'+ str(cube1.min()) + '\t\t' + str(cube2.min()))
print ('Max\t'+ str(cube1.max()) + '\t' + str(cube2.max()))


# Create 2D images
ratio_image = np.zeros((cube1.shape[1], cube1.shape[2]))
CNhi_image = np.zeros((cube1.shape[1], cube1.shape[2]))
CO_image = np.zeros((cube1.shape[1], cube1.shape[2]))

# Fill 2D images
for i in range(cube1.shape[1]):
    for j in range(cube1.shape[2]):

        spectrum_CNhi = cube1[:, i, j]
        spectrum_CO = cube2[:, i, j]

        CNhi_image[i, j] = spectrum_CNhi.max()
        CO_image[i, j] = spectrum_CO.max()

        if spectrum_CNhi.max() != 0:
            ratio_image[i, j] = spectrum_CO.max() / spectrum_CNhi.max()
        else:
            ratio_image[i, j] = np.nan


# Plot ratio image
plt.imshow(np.log10(ratio_image)-np.log10(ratio_image.min()))
plt.colorbar()

# Plot CO image
plt.imshow(CO_image)
cb = plt.colorbar()

# Plot CNhi image
plt.imshow(CNhi_image, vmin=cube2.min(), vmax=cube2.max())
plt.colorbar()

# global log(minimum) of ratio image
np.log10(ratio_image.min())

