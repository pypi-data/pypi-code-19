import time

from threading import Thread

from pypot.robot.sensor import Sensor
from rplidar import RPLidar


class RPLidarA2(Sensor):
    """
    Define a RPLidar sensor
    """
    registers = Sensor.registers + ['scan', 'mode']

    def __init__(self, name, mode):
        Sensor.__init__(self, name)

        self._lidar = RPLidar('/dev/ttyUSB0')
        self.mode = mode
        self._last_scan = []
        self.running = False
        
        

    def __repr__(self):
        return ('<LidarSensor name={self.name} '
                '{self.mesures} mesures >').format(self=self)
    
    @property
    def scan(self):
        return (self._timestamp, self._last_scan)
    
       
    @property
    def mesures(self):
        return len(self._last_scan)

    def _process_loop(self):
        for scan in self._lidar.iter_scans(scan_type=self.mode):
            self._last_scan = scan
            self._timestamp = time.time()
            if not self.running:
                break

    def start(self):
        self._processing = Thread(target=self._process_loop)
        self._processing.daemon = True
        self.running = True
        self._processing.start()
    
    def close(self):
        self.running = False
        try:
            self._processing.join()
        except AttributeError :
            pass
        self._lidar.stop()
        self._lidar.stop_motor()
