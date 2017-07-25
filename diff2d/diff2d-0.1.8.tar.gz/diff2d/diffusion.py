import sys, time

import matplotlib.pyplot as plt

from diff2d.core import load_data, simulation, plot_current_state

if __name__ == '__main__':
    # load the params
    img_path = sys.argv[1]
    D = float(sys.argv[2])
    dt = float(sys.argv[3])
    runs = int(sys.argv[4])

    # load the image
    img = load_data(img_path)
    print('Loaded matrix of %s; running simulation of %d * %f dt evolutions...' % (str(img.shape), runs, dt))

    # create the fig and ax
    fig, ax = plt.subplots(1, 2)
    plot_current_state(img, ax[0], 't0')

    # simulate
    t0 = time.time()
    diffused = simulation(img, runs, dt, D)
    t1 = time.time()

    # print and plot
    print('\n========================================\nCalculated {0} steps of dt = {1} sec in {2} sec.'.format(runs, dt, t1 - t0))
    plot_current_state(diffused, ax[1], 't0 + %.1f sec' % (runs * dt))

    plt.show()