import numpy as np

from pyltc import fields
from pyltc.frames import Frame, FrameFormat
from pyltc.audioutils import FrameDecoder

class Decoder(object):
    def __init__(self, **kwargs):
        self.frame_format = None
        self.frame = None
        self.data_block = fields.LTCDataBlock(generator=self)
    
