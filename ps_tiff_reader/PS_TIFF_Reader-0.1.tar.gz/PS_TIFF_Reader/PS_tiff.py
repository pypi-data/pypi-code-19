##
# Park Systems Imaging Library
#
# Simple TIFF read/writer
#

# TIFF Tags for Palette Color Image
WIDTH           = 256
LENGTH          = 257
BITSPERSAMPLE   = 258
COMPRESSION     = 259
PHOTO           = 262
STRIPOFFSETS    = 273
ROWSPERSTRIP    = 278
STRIPBYTECOUNTS = 279
XRESOLUTION     = 282
YRESOLUTION     = 283
RESOLUTIONUNIT  = 296
COLORMAP        = 320
DATETIME        = 306


# type, length
BYTE      = 1
ASCII     = 2
SHORT     = 3
LONG      = 4
RATIONAL  = 5
UNDEFINED = 7

TYPE_LENGTH = {BYTE:1, ASCII:1, SHORT:2, LONG:4, RATIONAL:8, UNDEFINED:1}

# string to integer (chr) and integer to string (ord) functions 
#ord32 = lambda x,o=0: ord(x[o]) + (ord(x[o+1])<<8) + (ord(x[o+2])<<16) + (ord(x[o+3])<<24)
#ord16 = lambda x,o=0: ord(x[o]) + (ord(x[o+1])<<8)
ord32 = lambda x,o=0: int(x[o] + x[o+1]*256 + x[o+2]*256*256 + x[o+3]*256*256*256)
ord16 = lambda x,o=0: int(x[o] + x[o+1]*256)


chr32 = lambda x: chr(x&0xff) + chr((x>>8)&0xff) + chr((x>>16)&0xff) + chr((x>>24)&0xff)
chr16 = lambda x: chr(x&0xff) + chr((x>>8)&0xff)

def __read_field(fp, typ, cnt, val):
    l = TYPE_LENGTH[typ] * cnt
    if l > 4:
        fp.seek(val)
        return fp.read(l)

    if TYPE_LENGTH[typ] == 1:
        return (val&0xff, (val>>8)&0xff, (val>>16)&0xff, (val>24)&0xff)
    if TYPE_LENGTH[typ] == 2:
        return (val&0xffff, (val>>16)&0xffff)
    return val

def read(fp):
    """read a tiff file and returns all image field directory dictionary.
    a key is a tag and the value is a tuple of (type, value)
    """
    fp.seek(0)

    # tiff header
    hdr = fp.read(4)
    if hdr[:2] != b'II':
        raise TypeError('not a TIFF file')
    
    # read IFDs
    fp.seek(ord32(fp.read(4)))
    nifds = ord16(fp.read(2))

    ifds = []
    for i in range(nifds):
        s = fp.read(12)
        ifds.append(s)

    fields = {}
    for s in ifds:
        tag = ord16(s,0)
        typ = ord16(s,2)
        cnt = ord32(s,4)
        val = ord32(s,8)

        fields[tag] = __read_field(fp, typ, cnt, val)

    return fields


def write_field(fp, offset, data):
    prev = fp.tell()
    fp.seek(offset)
    fp.write(data)
    offset = fp.tell()
    fp.seek(prev)

    return offset
    
def write(fp, data, ifds={}):
    """write a Park Systems Tiff file
      fp   : file pointer
      data : tiff image data (numpy array)
      ifds : image field dictionary. A key is a tag, the value is a tuple of (type, value or data)
    """
    h, w = data.shape
    
    # tiff strips
    nrow = 8192 / w
    nbyte = w * nrow

    length = h * w
    count = ''
    nstrip = 1 
    while (length > nbyte):
        count += chr32(nbyte)
        length -= nbyte
        nstrip += 1
    if length > 0:
        count += chr32(length)
        
    # IFD contents for Palette Color Images
    ifds[WIDTH]           = LONG,     chr32(w)
    ifds[LENGTH]          = LONG,     chr32(h)
    ifds[BITSPERSAMPLE]   = SHORT,    chr16(8)
    ifds[COMPRESSION]     = SHORT,    chr16(1)
    ifds[PHOTO]           = SHORT,    chr16(3)
    ifds[ROWSPERSTRIP]    = LONG,     chr32(nrow)
    ifds[STRIPBYTECOUNTS] = LONG,     count

    ifds[RESOLUTIONUNIT]  = SHORT,    chr16(2)
    
    # set up strip offsets
    # the tiff data will locate after ifds.
    offset = 26 + len(ifds) * 12
    offsets = ''
    for i in range(nstrip):
        offsets += chr32(offset + nbyte * i)
        
    ifds[STRIPOFFSETS]    = LONG, offsets
    
    ##
    # now write contents on the TIFF  
    fp.seek(0)

    # tiff header
    fp.write('II')
    fp.write(chr16(42))
    fp.write(chr32(8))
    
    # write data
    offset = write_field(fp, offset, data.astype('uint8').tostring())
    fp.write(chr16(len(ifds)))
    
    tags = ifds.keys()
    tags.sort()
    
    for tag in tags:
        typ, val = ifds[tag]
        fp.write(chr16(tag))
        fp.write(chr16(typ))
        fp.write(chr32(len(val) / TYPE_LENGTH[typ])) 
        if len(val) > 4:
            fp.write(chr32(offset))
            offset = write_field(fp, offset, val)
        else:
            val = val + '\0' * (4-len(val))
            fp.write(val)
            
    fp.write(chr32(0))    # next IFD offset. `0' means end of tag