from skimage.io import imread
from skimage import color
from numba import jit


def load_data(path):
    return color.rgb2gray(imread(path))


def plot_current_state(img, ax, title=None):
    ax.imshow(img, cmap='Reds')
    if title is not None:
        ax.set_title(title)


@jit
def evolve(u, dt, D):
    u2 = u.copy()
    M,N = u.shape
    for i in range(M):
        for j in range(N):
            grid_xx = u[(i+1)%M,j] + u[(i-1)%M,j] - 2.0 * u[i,j]
            grid_yy = u[i,(j+1)%N] + u[i,(j-1)%N] - 2.0 * u[i,j]
            u2[i,j] = u[i,j] + D * (grid_xx + grid_yy) * dt
    return u2


def simulation(img, runs, step, D):
    # create working copy
    u = img.copy()

    # evolve
    for _ in range(runs):
        # evolve the u
        u = evolve(u, step, D)

        # just writing
        if _ % 10 == 0:
            print('{0}%      '.format(round(_ / runs * 100), 1), end='\r')
    print('Done.      ')

    return u
