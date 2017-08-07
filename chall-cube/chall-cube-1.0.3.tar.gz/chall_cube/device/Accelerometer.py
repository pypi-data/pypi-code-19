from .adxl345 import ADXL345


class Accelerometer:

    def __init__(self):
        self.__adxl345 = ADXL345()
        self.__dice = [5, 4, 6, 2, 3, 1]

    def get_current_face(self):
        axes = self.__adxl345.getAxes(True)
        axes = [axes['x'], axes['y'], axes['z']]
        axesAbs = list(map(abs, axes))
        maxIndex = axesAbs.index(max(axesAbs))
        orientation = maxIndex

        if axes[maxIndex] < 0:
            orientation += 3

        return self.__dice[orientation]
