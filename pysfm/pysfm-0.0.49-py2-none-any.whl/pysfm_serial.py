__author__ = 'hclee'

import serial
import platform

if platform.system() == 'Windows':
    import serial.tools.list_ports_windows as ListPortInfo
if platform.system() == 'Linux':
    import serial.tools.list_ports_linux as ListPortInfo

# [hyeonchang.lee] test is required.
# elif platform.system() == 'Linux':
#     import serial.tools.list_ports_linux as ListPortInfo
# elif platform.system() == 'macosx':
#     import serial.tools.list_ports_osx as ListPortInfo


class PySFMComm:
    def __init__(self):
        self.comm = None
        self.baudrate = None
        self.is_open = None
        self.port = None

    def open(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate
        self.is_open = False

        if type(self.port) is int:
            self.port = 'COM' + str(port)

        try:
            if self.is_open is True:
                print 'already connected'
                self.comm.close()
                print 'closed'

            self.comm = serial.Serial(self.port, self.baudrate)

            if self.comm.isOpen():
                print 'opened'
                self.is_open = True
                return True

        except serial.SerialException as e:
            print(e)
            self.is_open = False
            return False

    def close(self):
        if self.is_open:
            self.comm.close()
        print 'closed'

    def get_list_port_info(self):
        list_port_info = ListPortInfo.comports()

        list_port = []
        for x in list_port_info:
            list_port.append(x.device)
        return list_port

    def get_baudrate_list(self):
        return [9600, 19200, 38400, 57600, 115200, 230400, 460800]

#unit test
if __name__ == '__main__':
    comm = PySFMComm()
    list_port = comm.get_list_port_info()

    print list_port