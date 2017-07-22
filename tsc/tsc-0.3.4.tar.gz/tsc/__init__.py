import pandas as pd
from array import array


from .algo import diff, diff_depth, undiff, undiff_depth
from .converter import (
    parse_csv, parse_df, to_internal,
    parse_internal, to_csv, to_np)


from zlib import compress as pack1, decompress as unpack1
from brotli import compress as pack2, decompress as unpack2
from paq import compress as pack3, decompress as unpack3
from bsc import compress as pack4, decompress as unpack4


__version__ = '0.3.4'


packs = [None, pack1, pack2, pack3]
modes = [None, 'zlib', 'brotli', 'paq']


# BSC is only as good as brotli if the file is large enough
# Brotli is very slow (at compressing) when file is large
# So we could combine the best part of both algorithm
# to create a better level2 algorithm
# Below we set the threshold to start using BSC
MIN_BSC_SIZE = 100000
MIN_BSC_LENGTH = 20000


def get_depth_params(headers):
    ts_cols = ['timestamp', 'pre_close',
               'open', 'high', 'low', 'close', 'price']
    if ('ap1' in headers and 'av1' in headers) or \
            ('bp1' in headers and 'bv1' in headers):
        if 'av1' in headers:
            offset = headers.index('av1') - headers.index('ap1')
        else:
            offset = headers.index('bv1') - headers.index('bp1')
        for i, h in enumerate(headers):
            if h.startswith('ap') and h[-1].isdigit():
                start = i
                break
            elif h.startswith('bp') and h[-1].isdigit():
                start = i
                break
        start = start + offset
        end = start + offset
        excludes = array('l')
        for i, h in enumerate(headers):
            if h not in ts_cols \
                    and not h[-1].isdigit():
                excludes.append(i)
        return excludes, start, end
    elif set(ts_cols) & set(headers):
        start = end = 0
        excludes = array('l')
        for i, h in enumerate(headers):
            if h not in ts_cols \
                    and not h[-1].isdigit():
                excludes.append(i)
        return excludes, start, end


def compress_bytes(v, level=2, precision=3):
    ncols, nrows, headers, divides, arr = parse_csv(v)
    params = get_depth_params(headers)
    if params:
        arr = diff_depth(ncols, nrows, arr, *params)
    else:
        arr = diff(ncols, nrows, arr)
    mode = modes[level] if level != 2 and len(arr) < MIN_BSC_LENGTH else 'bsc'
    data = to_internal(ncols, nrows, arr, headers, divides, mode)
    if level == 2 and len(data) > MIN_BSC_SIZE:
        return pack4(data)
    else:
        return packs[level](data)


def compress_dataframe(v, level=2, precision=3):
    ncols, nrows, headers, divides, arr = parse_df(v)
    params = get_depth_params(headers)
    if params:
        arr = diff_depth(ncols, nrows, arr, *params)
    else:
        arr = diff(ncols, nrows, arr)
    mode = modes[level] if level != 2 and len(arr) < MIN_BSC_LENGTH else 'bsc'
    data = to_internal(ncols, nrows, arr, headers, divides, mode)
    if level == 2 and len(data) > MIN_BSC_SIZE:
        return pack4(data)
    else:
        return packs[level](data)


def compress(v, level=2, precision=3):
    assert level in [1, 2, 3]
    if isinstance(v, str):
        v = v.encode('utf-8')

    if isinstance(v, bytes):
        return compress_bytes(v, level, precision)
    elif isinstance(v, pd.DataFrame):
        return compress_dataframe(v, level, precision)


def decompress(v, format='df'):
    if v[:2] == b'\x00c':
        internal = unpack3(v)
    elif v[:2] in [b'\x78\x01', b'\x78\x5e', b'\x78\x9c', b'\x78\xda']:
        internal = unpack1(v)
    else:
        try:
            internal = unpack4(v)
        except:
            try:
                internal = unpack2(v)
            except:
                raise ValueError('Unrecognized Format')
    if b'+' not in internal:
        # format error, return raw internal
        return internal
    else:
        ncols, nrows, headers, divides, arr = parse_internal(internal)
        params = get_depth_params(headers)
        if params:
            arr = undiff_depth(ncols, nrows, arr, *params)
        else:
            arr = undiff(ncols, nrows, arr)
        if format == 'csv':
            return to_csv(ncols, nrows, headers, divides, arr)
        elif format == 'df':
            arr = to_np(ncols, nrows, headers, divides, arr)
            return pd.DataFrame(arr)
        else:
            raise NotImplementedError('format {} not supported'.format(
                format))
