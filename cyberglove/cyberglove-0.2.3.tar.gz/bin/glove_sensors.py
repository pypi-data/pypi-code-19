import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation
from cyberglove import CyberGlove
from cyberglove.const import sensors_influence
import copy
import signal


class SubplotAnimation(animation.TimedAnimation):
    def __init__(self):
        self.glove = CyberGlove()
        fig = plt.figure(figsize=(15, 8))
        self.axs = []
        self.lines = []
        self.nsensors = len(sensors_influence)
        for idx in range(self.nsensors):
            ax = fig.add_subplot(4, 6, idx + 1)
            ax.set_xlabel('Sensor %d' % (idx))
            self.axs.append(ax)

            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_aspect('equal', 'datalim')
            line = Line2D([], [], color='black')
            self.lines.append(line)
            ax.add_line(line)

        animation.TimedAnimation.__init__(self, fig, interval=10, blit=True)
        self.datas = []

    def _draw_frame(self, framedata):
        data = copy.deepcopy(self.glove.read())
        data = np.array(data).astype(np.float32)
        self.datas.append(data)
        nlast = 50
        for line_idx, line in enumerate(self.lines):
            vals = np.stack(self.datas)
            vals -= np.min(vals, axis=0, keepdims=True)
            vals += 1e-4
            vals /= np.max(vals, axis=0, keepdims=True)
            vals *= 0.8
            vals += 0.1
            x = np.arange(vals[-nlast:].shape[0]) * 0.01
            y = vals[-nlast:, line_idx]
            line.set_data(x, y)

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(10))

    def _init_draw(self):
        for line in self.lines:
            line.set_data([], [])

def close(*args, **kwargs):
    exit(0)

signal.signal(signal.SIGINT, close)
signal.signal(signal.SIGTERM, close)

ani = SubplotAnimation()
plt.show()