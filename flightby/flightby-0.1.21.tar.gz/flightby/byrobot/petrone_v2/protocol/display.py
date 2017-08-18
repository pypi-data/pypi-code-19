import numpy as np
from struct import *
from enum import Enum

from flightby.communication.base import ISerializable



class Pixel(Enum):
    
    Black               = 0x00
    White               = 0x01



class Font(Enum):
    
    LiberationMono5x8   = 0x00
    LiberationMono10x16 = 0x01



class Align(Enum):
    
    Left                = 0x00      # 수동 조작
    Center              = 0x01      
    Right               = 0x02      




class ClearAll(ISerializable):

    def __init__(self):
        self.pixel       = Pixel.White


    @classmethod
    def getSize(cls):
        return 1


    def toArray(self):
        return pack('<B', self.pixel.value)


    @classmethod
    def parse(cls, dataArray):
        data = ClearAll()
        
        if len(dataArray) != cls.getSize():
            return None

        data.pixel = unpack('<B', dataArray)
        data.pixel = Pixel(data.pixel)
        
        return data



class Clear(ISerializable):

    def __init__(self):
        
        self.x           = 0
        self.y           = 0
        self.width       = 0
        self.height      = 0
        self.pixel       = Pixel.White


    @classmethod
    def getSize(cls):
        return 9


    def toArray(self):
        return pack('<hhhhB', self.x, self.y, self.width, self.height, self.pixel.value)


    @classmethod
    def parse(cls, dataArray):
        data = Clear()
        
        if len(dataArray) != cls.getSize():
            return None

        data.x, data.y, data.width, data.height, data.pixel = unpack('<hhhhB', dataArray)

        data.pixel = Pixel(data.pixel);
        
        return data



class Invert(ISerializable):

    def __init__(self):
        
        self.x           = 0
        self.y           = 0
        self.width       = 0
        self.height      = 0


    @classmethod
    def getSize(cls):
        return 8


    def toArray(self):
        return pack('<hhhh', self.x, self.y, self.width, self.height)


    @classmethod
    def parse(cls, dataArray):
        data = Invert()
        
        if len(dataArray) != cls.getSize():
            return None

        data.x, data.y, data.width, data.height = unpack('<hhhh', dataArray)
        
        return data



class DrawPoint(ISerializable):

    def __init__(self):
        
        self.x           = 0
        self.y           = 0
        self.pixel       = Pixel.White


    @classmethod
    def getSize(cls):
        return 5


    def toArray(self):
        return pack('<hhB', self.x, self.y, self.pixel.value)


    @classmethod
    def parse(cls, dataArray):
        data = DrawPoint()
        
        if len(dataArray) != cls.getSize():
            return None

        data.x, data.y, data.pixel = unpack('<hhB', dataArray)

        data.pixel = Pixel(data.pixel);
        
        return data



class DrawRect(ISerializable):

    def __init__(self):
        
        self.x          = 0
        self.y          = 0
        self.width      = 0
        self.height     = 0
        self.pixel      = Pixel.White
        self.flagFill   = True


    @classmethod
    def getSize(cls):
        return 10


    def toArray(self):
        return pack('<hhhhB?', self.x, self.y, self.width, self.height, self.pixel.value, self.flagFill)


    @classmethod
    def parse(cls, dataArray):
        data = DrawRect()
        
        if len(dataArray) != cls.getSize():
            return None

        data.x, data.y, data.width, data.height, data.pixel, data.flagFill = unpack('<hhhhB?', dataArray)

        data.pixel = Pixel(data.pixel);
        
        return data



class DrawCircle(ISerializable):

    def __init__(self):
        
        self.x          = 0
        self.y          = 0
        self.radius     = 0
        self.pixel      = Pixel.White
        self.flagFill   = True


    @classmethod
    def getSize(cls):
        return 8


    def toArray(self):
        return pack('<hhhB?', self.x, self.y, self.radius, self.pixel.value, self.flagFill)


    @classmethod
    def parse(cls, dataArray):
        data = DrawCircle()
        
        if len(dataArray) != cls.getSize():
            return None

        data.x, data.y, data.radius, data.pixel, data.flagFill = unpack('<hhhB?', dataArray)

        data.pixel = Pixel(data.pixel);
        
        return data



class DrawString(ISerializable):

    def __init__(self):
        
        self.x          = 0
        self.y          = 0
        self.font       = Font.LiberationMono5x8
        self.pixel      = Pixel.White
        self.message    = ""


    @classmethod
    def getSize(cls):
        return 6

    def toArray(self):
        dataArray = []
        dataArray.extend(pack('<hhBB', self.x, self.y, self.font.value, self.pixel.value))
        dataArray.extend(self.message.encode('ascii', 'ignore'))
        return dataArray


    @classmethod
    def parse(cls, dataArray):
        data = DrawString()
        
        if len(dataArray) <= cls.getSize():
            return None

        data.x, data.y, data.font, data.pixel = unpack('<hhBB', dataArray[0:getSize()])
        data.font = Font(data.font);
        data.pixel = Pixel(data.pixel);
        data.message = dataArray[getSize():len(dataArray)].decode()
        
        return data



class DrawStringAlign(ISerializable):

    def __init__(self):
        
        self.x_start    = 0
        self.x_end      = 0
        self.y          = 0
        self.align      = Align.Center
        self.font       = Font.LiberationMono5x8
        self.pixel      = Pixel.White
        self.message    = ""


    @classmethod
    def getSize(cls):
        return 9


    def toArray(self):
        dataArray = []
        dataArray.extend(pack('<hhhBBB', self.x_start, self.x_end, self.y, self.align.value, self.font.value, self.pixel.value))
        dataArray.extend(self.message.encode('ascii', 'ignore'))
        return dataArray
    

    @classmethod
    def parse(cls, dataArray):
        data = DrawStringAlign()
        
        if len(dataArray) <= cls.getSize():
            return None

        data.x_start, data.x_end, data.y, data.align, data.font, data.pixel, data.message = unpack('<hhhBBBs', dataArray[0:getSize()])
        data.align = Align(data.align);
        data.font = Font(data.font);
        data.pixel = Pixel(data.pixel);
        data.message = dataArray[getSize():len(dataArray)].decode()
        
        return data
