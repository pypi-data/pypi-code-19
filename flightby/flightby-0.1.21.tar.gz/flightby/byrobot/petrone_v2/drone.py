import serial
import binascii
import random
import queue
import threading
from threading import Thread
from time import sleep
from struct import *

from flightby.byrobot.petrone_v2.receiver import *
from flightby.byrobot.petrone_v2.storage import *
from flightby.byrobot.petrone_v2.protocol import *
from flightby.byrobot.petrone_v2.protocol.base import *
from flightby.communication.base import *
from flightby.communication.crc import *



class Drone:


    def __init__(self):
        
        self.serialport      = None
        self.bufferReceive   = []
        self.bufferHandler   = []
        self.index           = 0

        self.threadLock      = threading.Lock()
        self.flagThreadRun   = False

        self.receiver        = Receiver()
        self.storage         = Storage()


    def _receiving(self):
        while self.flagThreadRun:
            
            self.threadLock.acquire()        # Get lock to synchronize threads
            self.bufferReceive.extend(self.serialport.read())
            self.threadLock.release()        # Free lock to release next thread

            sleep(0.001)


    def open(self, portname):
        self.serialport = serial.Serial(
            port = portname,
            baudrate = 115200,
            parity = serial.PARITY_NONE,
            stopbits = serial.STOPBITS_ONE,
            bytesize = serial.EIGHTBITS,
            timeout = 0)

        if( self.serialport.isOpen() ):
            self.flagThreadRun = True
            Thread(target=self._receiving, args=()).start()


    def close(self):
        self.flagThreadRun = False
        sleep(0.002)
        while (self.serialport.isOpen() == True):
            self.serialport.close()
            sleep(0.002)


    def makeTransferDataArray(self, header, data):
        if (header == None) or (data == None):
            return None

        if (not isinstance(header, Header)) or (not isinstance(data, ISerializable)):
            return None

        crc16 = CRC16.calc(header.toArray(), 0)
        crc16 = CRC16.calc(data.toArray(), crc16)

        dataArray = []
        dataArray.extend((0x0A, 0x55))
        dataArray.extend(header.toArray())
        dataArray.extend(data.toArray())
        dataArray.extend(pack('H', crc16))

        #print("{0} / {1}".format(len(dataArray), dataArray))

        return dataArray


    def transfer(self, header, data):
        if (self.serialport == None) or (self.serialport.isOpen() == False):
            return

        dataArray = self.makeTransferDataArray(header, data)

        self.serialport.write(dataArray)

        return dataArray


    def check(self):
        if len(self.bufferReceive) > 0:
            self.threadLock.acquire()           # Get lock to synchronize threads
            self.bufferHandler.extend(self.bufferReceive)
            self.bufferReceive.clear()
            self.threadLock.release()            # Free lock to release next thread

            while len(self.bufferHandler) > 0:
                self.receiver.call(self.bufferHandler[0])
                del(self.bufferHandler[0])
                
                if self.receiver.state == StateLoading.Loaded:
                    self.handler(self.receiver.header, self.receiver.dataBuffer)
                    self.receiver.checked()
                    return self.receiver.header.dataType

        return DataType.None_



    def handler(self, header, dataArray):
        if header.dataType == DataType.Ack:
            self.storage.countAck += 1



    # OLED 제어 명령들
    def sendDisplayClearAll(self, pixel):
        
        if ( not isinstance(pixel, display.Pixel) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayClear
        header.length   = display.ClearAll.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.ClearAll()

        data.pixel      = pixel

        return self.transfer(header, data)
    


    def sendDisplayClear(self, x, y, width, height, pixel):
        
        if ( not isinstance(pixel, display.Pixel) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayClear
        header.length   = display.Clear.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.Clear()

        data.x          = x
        data.y          = y
        data.width      = width
        data.height     = height
        data.pixel      = pixel

        return self.transfer(header, data)



    def sendDisplayInvert(self, x, y, width, height):
        
        header = Header()
        
        header.dataType = DataType.DisplayInvert
        header.length   = display.Invert.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.Invert()

        data.x          = x
        data.y          = y
        data.width      = width
        data.height     = height

        return self.transfer(header, data)



    def sendDisplayDrawPoint(self, x, y, pixel):
        
        if ( not isinstance(pixel, display.Pixel) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayDrawPoint
        header.length   = display.DrawPoint.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.DrawPoint()

        data.x          = x
        data.y          = y
        data.pixel      = pixel

        return self.transfer(header, data)



    def sendDisplayDrawRect(self, x, y, width, height, pixel, flagFill):
        
        if ( (not isinstance(pixel, display.Pixel)) or (not isinstance(flagFill, bool)) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayDrawRect
        header.length   = display.DrawRect.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.DrawRect()

        data.x          = x
        data.y          = y
        data.width      = width
        data.height     = height
        data.pixel      = pixel
        data.flagFill   = flagFill

        return self.transfer(header, data)



    def sendDisplayDrawCircle(self, x, y, radius, pixel, flagFill):
        
        if ( (not isinstance(pixel, display.Pixel)) or (not isinstance(flagFill, bool)) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayDrawCircle
        header.length   = display.DrawCircle.getSize()
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.DrawCircle()

        data.x          = x
        data.y          = y
        data.radius     = radius
        data.pixel      = pixel
        data.flagFill   = flagFill

        return self.transfer(header, data)



    def sendDisplayDrawString(self, x, y, font, pixel, message):
        
        if ( (not isinstance(font, display.Font)) or (not isinstance(pixel, display.Pixel)) or (not isinstance(message, str)) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayDrawString
        header.length   = display.DrawString.getSize() + len(message)
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.DrawString()

        data.x          = x
        data.y          = y
        data.font       = font
        data.pixel      = pixel
        data.message    = message

        return self.transfer(header, data)



    def sendDisplayDrawStringAlign(self, x_start, x_end, y, align, font, pixel, message):
        
        if ( (not isinstance(align, display.Align)) or (not isinstance(font, display.Font)) or (not isinstance(pixel, display.Pixel)) or (not isinstance(message, str)) ):
            return None

        header = Header()
        
        header.dataType = DataType.DisplayDrawStringAlign
        header.length   = display.DrawStringAlign.getSize() + len(message)
        header.from_    = DeviceType.Tester
        header.to_      = DeviceType.Controller
        
        data = display.DrawStringAlign()

        data.x_start    = x_start
        data.x_end      = x_end
        data.y          = y
        data.align      = align
        data.font       = font
        data.pixel      = pixel
        data.message    = message

        return self.transfer(header, data)


