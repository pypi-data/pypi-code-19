import lzma
import pickle

import logging
import numpy as np

from os import unlink, makedirs
from os.path import join, exists, dirname, basename
from bgparsers import readers


SEGMENT_SIZE_MIN = 10000
SEGMENT_SIZE = 2000000


def unify_column(values):
    val = values[0]
    for v in values:
        if v != val:
            return values
    return val


def minify_column(values):
    i = 0
    meta = {}

    result = []
    for v in values:
        if v not in meta:
            meta[v] = i
            i += 1
        result.append(meta[v])

    meta_list = [None] * i
    for k, v in meta.items():
        meta_list[v] = k

    # NumPY data types
    # uint8     Unsigned integer(0 to 255)
    # uint16    Unsigned integer(0 to 65535)
    # uint32    Unsigned integer(0 to 4294967295)
    # uint64    Unsigned integer(0 to 18446744073709551615)

    size = len(meta_list)
    if size <= 256:
        dtype = np.uint8
    elif size <= 65536:
        dtype = np.uint16
    else:
        dtype = np.uint32

    return meta_list, np.array(result, dtype=dtype)


def store_chunk(chunk, output_path, results, length):

    file_path = join(output_path, "c{:06d}.bgvars.xz".format(chunk))

    for k in results:
        results[k] = unify_column(results[k])

    values = {}
    for k in results:
        if isinstance(results[k], list):
            values[k], results[k] = minify_column(results[k])

    out_data = {
        'length': length,
        'data': values,
        'vectors': results
    }

    if len(results) > 0:
        try:
            with lzma.open(file_path, 'wb') as fd:
                pickle.dump(out_data, fd)
        except Exception as e:
            if exists(file_path):
                unlink(file_path)
            raise RuntimeError(e)


def run(input_selection, output_folder=None, force=False, exist_ok=False):
    input_file, input_annotations = input_selection

    if output_folder is None:
        output_folder = join(dirname(input_file), "bgvariants", "preprocess", basename(input_file))

    if force or not exists(output_folder):
        results = {}
        c = 0
        chunk = 0

        seg_size = None
        makedirs(output_folder, exist_ok=True)
        for r in readers.variants(input_file, annotations=input_annotations, extra=True):

            if seg_size is None:
                seg_size = max(SEGMENT_SIZE / (len(r) / 8), SEGMENT_SIZE_MIN)

            for k in r.keys():
                if k not in results:
                    results[k] = [None]*c
            for k in results.keys():
                results[k].append(r.get(k, None))
            c+=1

            if c >= seg_size:
                store_chunk(chunk, output_folder, results, c)
                chunk += 1
                c = 0
                results = {}

        if c > 0:
            store_chunk(chunk, output_folder, results, c)
    else:
        if exist_ok:
            logging.warning("Preprocessed folder '{}' already exists".format(basename(output_folder)))
        else:
            raise FileExistsError("Preprocess folder '{}' already exists".format(output_folder))

