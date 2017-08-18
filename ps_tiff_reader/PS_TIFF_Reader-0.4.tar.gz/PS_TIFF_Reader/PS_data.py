"""Park Systems TIFF"""
name = 'tiff'

from PS_TIFF_Reader import PS_package
from PS_package import pack, unpack
from datetime import datetime

from matplotlib import cm
from numpy import asarray, vstack, fromstring, flipud

from PS_TIFF_Reader import PS_tiff as _tiff

MAGIC    = 50432
VERSION  = 50433
DATA     = 50434
HEADER   = 50435
COMMENTS = 50436
PDD      = 50440

empty = []


HEADER_STRUCT = (('i',    'type',          'image',     ['image', 'line profile', 'spectroscopy']),
                 ('64s',  'source',        'unknown',   empty),
                 ('16s',  'head mode',     'unknown',   empty),
                 ('d',    'LPF',           0.0,         empty),
                 ('i',    'is_flatten?',   False,       [False, True]),
                 ('i',    'is_AC_track?',  False,       [False, True]),
                 ('i',    'width',         256,         empty),
                 ('i',    'height',        256,         empty),
                 ('d',    'angle',         0,           empty),
                 ('i',    'is_sine_scan?', False,       [False, True]),
                 ('d',    'overscan',      0.0,         []),
                 ('i',    'scan_dir_x',    'to left',   ['to left', 'to right']),
                 ('i',    'scan_dir_y',    'to top',    ['to bottom', 'to top']),
                 ('i',    'fast_scan_axis','x',         ['x', 'y']),
                 ('d',    'x_size',        0.0,         empty),
                 ('d',    'y_size',        0.0,         empty),
                 ('d',    'x_center',      0.0,         empty),
                 ('d',    'y_center',      0.0,         empty),
                 ('d',    'scan_rate',     1.0,         empty),
                 ('d',    'set_point',     0.0,         empty),
                 ('16s',  'set_point_unit','nm',        empty),
                 ('d',    'tip_bias',      0.0,         empty),
                 ('d',    'sample_bias',   0.0,         empty),
                 ('d',    'data_gain',     1.0,         empty),
                 ('d',    'data_scale',    1.0,         empty),
                 ('d',    'data_offset',   0.0,         empty),
                 ('16s',  'z_unit',        'um',        empty),
                 ('i',    'cmap_min',      0,           empty),
                 ('i',    'cmap_max',      0,           empty),
                 ('i',    'cmap_mean',     0,           empty),
                 ('i',    'compression',   0,           empty),
                 ('i',    'is_log_scale?', False,       [False, True]),
                 ('i',    'is_square?',    False,       [False, True]),
                 ('d',    'z_gain',        1.0,         empty),
                 ('d',    'z_range',       0,           empty),
                 ('16s',  'xy_mode',       'unknown',   empty),
                 ('16s',  'z_mode',        'unknown',   empty),
                 ('16s',  'xy_servo',      'unknown',   empty),
                 ('i',    'data_type',     'int16',   ['int16', 'int32', 'float32']),
                 ('i',    'x_pdd',         0,           empty),
                 ('i',    'y_pdd',         0,           empty),
                 ('220s', 'Reserved',      '',          empty))

PDD_STRUCT = (('i', 'pixel',   4,      empty),
              ('d', 'size',     1.0,    empty),
              ('d', 'center',   0.0,    empty))

def __points(npixel, offset, size, npdd, tag, s=0):
    pos = [offset-size/2.]
    pxl = [0.]

    if npdd > 0:
        tot = npixel-1
        for i in range(npdd):
            p = unpack(tag[PDD][s:s+20], PDD_STRUCT)
            s = s + 20
            pos.append(p['center'] + offset - p['size'] / 2.0)
            pxl.append(p['pixel'])
            tot = tot - p['pixel']

        pos.append(p['center'] + offset + p['size'] / 2.0)
        n = round((pos[1] - pos[0]) / (size - pos[-1] + pos[1]) * tot)
        pxl.insert(1, n)

        for i in range(1,len(pxl)):
            pxl[i] = pxl[i] + pxl[i-1]

        pos.append(offset+size/2.)
        pxl.append(npixel-1)

    else:
        pos.append(offset+size)
        pxl.append(1.)

    pos = asarray(pos, dtype='float')
    pxl = asarray(pxl, dtype='float')

    ptp = pos.ptp()
    if ptp == 0:
        ptp = 1

    return (pos - pos[0]) / ptp, (pxl - pxl[0]) / pxl.ptp(), s

def __xy_points(header, tag):
    h, w = header['height'], header['width']

    xs, ys = header['x_size'], header['y_size']
    xc, yc = header['x_center'], header['y_center']
    nx, ny = header['x_pdd'], header['y_pdd']

    x0 = xs / 2.0 - xc
    y0 = ys / 2.0 - yc

    s = 0
    pos, pxl, s = __points(w, x0, xs, nx, tag, s)
    header['x_points'] = vstack((pos, pxl)).T
    pos, pxl, s = __points(h, y0, ys, ny, tag, s)
    header['y_points'] = vstack((pos, pxl)).T

    header['x_offset'] = -x0
    header['y_offset'] = -y0

def tiff_read(fp): 
    fp = open(fp, 'rb')
    data, header = load(fp)
    fp.close()
    return data, header

def load(fp):

    tag = _tiff.read(fp)
    if tag[MAGIC] != 0x0E031301 and tag[VERSION] < 0x01000001:
        raise TypeError('not a Park Systems TIFF')

    # unpacking header
    header = unpack(tag[HEADER], HEADER_STRUCT)

    # data
    h, w = header['height'], header['width']
    data = fromstring(tag[DATA], dtype=header['data_type'])
    data = (data.astype('float') * header['data_gain']).reshape(h,w)

    # color map
    cmap = fromstring(tag[_tiff.COLORMAP], dtype='uint16').reshape(3,256)
    header['color_map'] = cmap.T

    # insert created date
    try:
        header['date_time'] = datetime.strptime(tag[_tiff.DATETIME][:-1], '%Y:%m:%d %H:%M:%S')
    except:
        pass

    __xy_points(header, tag)
    

    # delete unused items
    del header['height']
    del header['width']
    del header['data_type']
    del header['data_gain']
    del header['data_scale']
    del header['data_offset']
    del header['cmap_min']
    del header['cmap_max']
    del header['cmap_mean']
    del header['x_center']
    del header['y_center']
    del header['x_pdd']
    del header['y_pdd']

    return data, header
    



def save(fp, data, **header):
    h, w = data.shape

    # AFM data
    M, m = data.max(None), data.min(None)
    scale  = 32767. / max(abs(M), abs(m))
    z = (data * scale).astype('int16')

    # color map
    cmap = header.get('color_map', (cm.jet(range(256))[:,:3] * 65535.0)).T

    # header
    header['width']     = w
    header['height']    = h
    header['x_center']  = header.get('x_offset',0) + header.get('x_size', w) / 2.0
    header['y_center']  = header.get('y_offset',0) + header.get('y_size', h) / 2.0
    header['data_gain'] = 1.0 / scale
    header['cmap_min']  = round(z.min(None))
    header['cmap_max']  = round(z.max(None))
    header['cmap_mean'] = round(z.mean(None))

    dpi = header.get('dpi', (96, 96))


    # Park Systems specific setup image file directory
    ifds = {}
    ifds[_tiff.XRESOLUTION] = _tiff.RATIONAL, _tiff.chr32(dpi[0]) + _tiff.chr32(1)
    ifds[_tiff.YRESOLUTION] = _tiff.RATIONAL, _tiff.chr32(dpi[1]) + _tiff.chr32(1)
    ifds[_tiff.COLORMAP]    = _tiff.SHORT,    cmap.astype('uint16').tostring()
    ifds[_tiff.DATETIME]    = _tiff.ASCII,    header.get('date_time', datetime.now()).strftime('%Y:%m:%d %H:%M:%S')

    ifds[MAGIC]             = _tiff.LONG,     _tiff.chr32(0x0E031301)
    ifds[VERSION]           = _tiff.LONG,     _tiff.chr32(0x01000002)
    ifds[HEADER]            = _tiff.BYTE,     pack(header, HEADER_STRUCT)
    ifds[DATA]              = _tiff.BYTE,     z.tostring()

    _tiff.write(fp, flipud((z - z.mean(None)) / (z.ptp(None)) * 127 + 128), ifds)

