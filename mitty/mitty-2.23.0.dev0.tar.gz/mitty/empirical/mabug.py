import matplotlib.pyplot as plt
import numpy as np

a = np.random.randn(1000)
b = np.random.randn(1000)

a_ma = np.ma.masked_where(a > 0, a)
b_ma = np.ma.masked_where(b < 0, b)

# a[a > 0] = np.nan
# b[b < 0] = np.nan
#
# a_ma = np.ma.masked_where(np.isnan(a), a)
# b_ma = np.ma.masked_where(np.isnan(b), b)

bins = np.arange(-3,3.25,0.25)

fig, ax = plt.subplots(1,3, figsize=(10,3), subplot_kw={'aspect': 1})

hist, xbins, ybins, im = ax[0].hist2d(a_ma,b_ma, bins=bins, normed=True)

hist, xbins, ybins = np.histogram2d(a_ma,b_ma, bins=bins, normed=True)
extent = [xbins.min(),xbins.max(),ybins.min(),ybins.max()]

im = ax[1].imshow(hist.T, interpolation='none', origin='lower', extent=extent)
im = ax[2].imshow(np.ma.masked_where(hist == 0, hist).T, interpolation='none', origin='lower', extent=extent)

ax[0].set_title('mpl')
ax[1].set_title('numpy')
ax[2].set_title('numpy masked')