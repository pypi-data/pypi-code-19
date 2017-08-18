import time

from flightby.byrobot.petrone_v2.protocol.base import *
from flightby.communication.base import ISerializable
from flightby.communication.base import StateLoading
from flightby.communication.base import Section
from flightby.communication.crc import CRC16



class Receiver:


    def __init__(self):
        
        self.state                   = StateLoading.Ready
        self.sectionOld              = Section.End
        self.section                 = Section.Start
        self.index                   = 0

        self.header                  = Header()
        self.timeReceiveStart        = 0
        self.timeReceiveComplete     = 0

        self.dataBuffer              = []

        self.crc16received           = 0
        self.crc16calculated         = 0


    def call(self, data):
        
        now = time.clock() * 1000


        # First Step
        if self.state == StateLoading.Ready:
            self.section = Section.Start
            self.index = 0

        elif self.state == StateLoading.Receiving:
            if self.timeReceiveStart + 100 < now:
                self.state = StateLoading.Ready
                self.section = Section.Start
                self.index = 0

        elif self.state == StateLoading.Loaded:
            return


        # Second Step
        if self.section != self.sectionOld:
            self.index = 0
            self.sectionOld = self.section
        

        # Third Step
        if self.section == Section.Start:
            if self.index == 0:
                if data == 0x0A:
                    self.state = StateLoading.Receiving
                else:
                    self.state = StateLoading.Failure
                self.timeReceiveStart = now

            elif self.index == 1:
                if data != 0x55:
                    self.state = StateLoading.Failure
                else:
                    self.section = Section.Header
            else:
                self.state = StateLoading.Failure
        
        elif self.section == Section.Header:
            if self.index == 0:
                self.header = Header()
                self.header.dataType = DataType(data)
                self.crc16calculated = CRC16.calc(data, 0)
            elif self.index == 1:
                self.header.length = data
                self.crc16calculated = CRC16.calc(data, self.crc16calculated)
            elif self.index == 2:
                self.header.from_ = DeviceType(data)
                self.crc16calculated = CRC16.calc(data, self.crc16calculated)
            elif self.index == 3:
                self.header.to_ = DeviceType(data)
                self.crc16calculated = CRC16.calc(data, self.crc16calculated)

                if self.header.length > 128:
                    self.state = StateLoading.Failure
                elif self.header.length == 0:
                    self.section = Section.End
                else:
                    self.section = Section.Data
                    self.dataBuffer.clear()
            else:
                self.state = StateLoading.Failure
        
        elif self.section == Section.Data:
            self.dataBuffer.append(data)
            self.crc16calculated = CRC16.calc(data, self.crc16calculated)

            if (self.index == self.header.length - 1):
                self.section = Section.End
        
        elif self.section == Section.End:
            if self.index == 0:
                self.crc16received = data
            elif self.index == 1:
                self.crc16received = (data << 8) | self.crc16received

                if self.crc16received == self.crc16calculated:
                    self.timeReceiveComplete = now
                    self.state = StateLoading.Loaded
                else:
                    self.state = StateLoading.Failure
            else:
                self.state = StateLoading.Failure

        else:
            self.state = StateLoading.Failure


        #Forth Step
        if self.state == StateLoading.Receiving:
            self.index += 1
        elif self.state == StateLoading.Failure:
            self.state = StateLoading.Ready


    def checked(self):
        self.state = StateLoading.Ready


