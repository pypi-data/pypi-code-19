import re
import os
import time
import struct
from serial import Serial
import serial
import serial.tools.list_ports
# import serial.tools.list_ports_windows
# from multiprocessing import Array, Lock, Queue, queues
# from multiprocessing import Process
from threading import Thread
from queue import Queue, Empty
import numpy as np
import pickle
from cyberglove.const import joint_names, data_dir


def find_port(timeout=None):
    '''
    Heuristics for finding what serial port a cyberglove is on.
    '''
    results = []
    start = time.time()
    while len(results) == 0:
        print('Searching for serial port ...')
        time.sleep(.5)
        ports = serial.tools.list_ports.comports()
        # USB FTDI device, and serial number starts with the letter 'A'
        results = [p.device for p in ports if 'VID:PID=0403:6001' in p.hwid]
        if time.time() > start + 10:
            raise Exception('Failed to find cyberglove serial port.\n' +
                            'Is the glove plugged in and turned on?')
    if len(results) > 1:
        print("WARNING: more than one cyberglove found, using first")
    return Serial(results[0],
                  timeout=timeout,
                  write_timeout=None,
                  inter_byte_timeout=None,
                  baudrate=115200,
                  exclusive=True)


class CyberGlove():
    _time_regex = b'..:..:..:..:.S'
    _packet = '>xxxxxxxxxxxxxxHHHHHHHHHHHHHHHHHHHHHHxxx'  # packet byte structure
    _packet_len = struct.calcsize(_packet)

    def __init__(self):
        print("Initializing cyberglove.")
        self._queue = Queue(maxsize=1)
        self._thread = Thread(target=self._reader, args=(self._queue,))
        self._thread.daemon = True
        self._thread.start()
        self._mapping = None  # Calibration, will be loaded if needed

    def read(self, block=True, timeout=None):
        '''
        Use both a deque and a queue to get both update-insert (deque)
        and blocking (queue).
        '''
        return self._queue.get(block=block, timeout=timeout)

    def read2shadow(self, block=True, timeout=None):
        '''
        Reads the glove sesors and maps them to
        shadow hand joints.
        '''
        if self._mapping is None:
            OPENAI_USER = os.getenv('OPENAI_USER', 'OPENAI_USER')
            mapping_file = os.path.join(data_dir, "mapping_%s.pkl" % OPENAI_USER)
            print("Loading cyberglove mapping from: %s" % mapping_file)
            if os.path.exists(mapping_file):
                with open(mapping_file, "rb") as f:
                    self._mapping = pickle.load(f)
            else:
                recordings_file = os.path.join(data_dir, 'recordings_%s.pkl' % OPENAI_USER)
                if os.path.exists(recordings_file):
                    raise Exception("Recordings exist, but calibration mapping is missing.\n" +
                                    "recording file: (found) {}\n".format(recordings_file) +
                                    "mapping file: (not found {})\n".format(mapping_file) +
                                    "Run `fit_mapping.py` to generate mapping.\n" +
                                    "See cyberglove README.md for more info.")
                raise Exception("You have to record calibration for cyberglove.\n" +
                                "mapping file: (not found) {}\n".format(mapping_file) +
                                "Execute `gather_recordings.py` to gather data from cyberglove.\n" +
                                "See cyberglove README.md for more info.")
        return dict(zip(joint_names, self._mapping.map(self.read(block=block, timeout=timeout))))

    def _reader(self, queue):
        print('starting cyberglove streaming thread')
        self._last_resync = 0
        self._port = find_port(timeout=1)
        self._port.flush()
        time.sleep(0.1)  # wait for data if necessary
        if self._port.read(self._packet_len):
            print('Port currently streaming data')
        else:
            print('starting cyberglove streaming')
            self._port.write(b'1E4010111\0')
            self._port.flush()
            self._port.write(b'1S\0')
        self._port.flush()
        time.sleep(0.5)
        while True:
            data = self._port.read(self._packet_len)
            if not re.match(self._time_regex, data):
                data = self._sync()
            packet = struct.unpack(self._packet, data)
            try:
                queue.get_nowait()  # empty item in queue if present
            except Empty:
                pass
            queue.put(packet)
            time.sleep(0)  # yield CPU

    def _sync(self):
        ''' Recover an out-of-sync stream, returning a packet after sync '''
        find = None
        while find is None:
            print('Re-synching data stream')
            if time.time() - self._last_resync < .5:
                print("Re-syncing occurred twice within a sec.")
                raise Exception('Unplug and plug your cyberglove. Quitting')
            self._last_resync = time.time()
            data = self._port.read(2 * self._packet_len)
            find = re.search(self._time_regex, data)
        self._port.read(find.start())  # Dump remainder bytes
        return self._port.read(self._packet_len)  # return next packet

    def _close_port(self, *args, **kwargs):
        # Active waiting for process to finish.
        if hasattr(self, "_port") and self._port.is_open:
            self._port.write(b'\x03')
            self._port.flush()
            self._port.close()


if __name__ == '__main__':
    cg = CyberGlove()
    try:
        cg.read(timeout=5)
    except Empty:
        print('Cyberglove failed to start.  Unplug and replug it.')
        exit(1)
    count = 0
    start = time.time()
    max_val = np.array(cg.read())
    min_val = np.array(cg.read())
    loop_time = 0
    while cg._thread.isAlive():
        loop_start = time.time()
        data = cg.read(timeout=5)
        max_val = np.maximum(np.array(data), max_val)
        min_val = np.minimum(np.array(data), min_val)
        count += 1
        print_start = time.time()
        print("data:", data)
        print("max : %s" % max_val.tolist())
        print("min : %s" % min_val.tolist())
        print("loop time", loop_time)
        print("times per sec: %f" % (count / (time.time() - start)))
        if os.name == 'nt':
            print("(On windows times per sec is slow because print() is slow)")
            print("(loop time to determine read speed and not times per sec)")
        loop_time = time.time() - loop_start
