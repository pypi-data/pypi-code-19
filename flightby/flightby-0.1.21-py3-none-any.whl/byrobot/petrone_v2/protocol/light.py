import numpy as np
from struct import *
from enum import Enum

from flightby.communication.base import ISerializable



class DroneMode(Enum):
    
    None_               = 0x00

    EyeNone             = 0x10
    EyeManual           = 0x11      # 수동 제어
    EyeHold             = 0x12      # 지정한 색상을 계속 켬
    EyeFlicker          = 0x13      # 깜빡임			
    EyeFlickerDouble    = 0x14      # 깜빡임(두 번 깜빡이고 깜빡인 시간만큼 꺼짐)			
    EyeDimming          = 0x15      # 밝기 제어하여 천천히 깜빡임

    ArmNone             = 0x40
    ArmManual           = 0x41      # 수동 제어
    ArmHold             = 0x42      # 지정한 색상을 계속 켬
    ArmFlicker          = 0x43      # 깜빡임			
    ArmFlickerDouble    = 0x44      # 깜빡임(두 번 깜빡이고 깜빡인 시간만큼 꺼짐)			
    ArmDimming          = 0x45      # 밝기 제어하여 천천히 깜빡임

    TailNone            = 0x70
    TailManual          = 0x71      # 수동 제어
    TailHold            = 0x72      # 지정한 색상을 계속 켬
    TailFlicker         = 0x73      # 깜빡임			
    TailFlickerDouble   = 0x74      # 깜빡임(두 번 깜빡이고 깜빡인 시간만큼 꺼짐)			
    TailDimming         = 0x75      # 밝기 제어하여 천천히 깜빡임

    EndOfType           = 0x76



class DroneFlags(Enum):
    
    None_               = 0x00

    EyeRed              = 0x80
    EyeGreen            = 0x40
    EyeBlue             = 0x20

    ArmRed              = 0x10
    ArmGreen            = 0x08
    ArmBlue             = 0x04



class ControllerMode(Enum):
    
    None_               = 0x00

    TeamNone            = 0x10
    TeamManual          = 0x11      # 수동 조작
    TeamHold            = 0x12      
    TeamFlicker         = 0x13      
    TeamFlickerDouble   = 0x14      
    TeamDimming         = 0x15      

    EndOfType           = 0x16      



class ControllerFlags(Enum):
    
    None_               = 0x00

    Red                 = 0x80
    Green               = 0x40
    Blue                = 0x20



class Mode(ISerializable):

    def __init__(self):
        self.mode        = 0
        self.interval    = 0


    @classmethod
    def getSize(cls):
        return 3


    def toArray(self):
        return pack('BH', self.mode, self.interval)


    @classmethod
    def parse(cls, dataarray):
        mode = Mode()
        
        if len(dataarray) == cls.getSize():
            mode.mode, mode.interval = unpack('BH', dataarray)

        return mode

