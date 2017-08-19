import logging
import pickle

def init_logger(level):
    logging.basicConfig(
        level=level,
        format='%(name)-12s: %(levelname)-8s %(message)s',
    )

def pack_data(filepaths):
    data = (filepaths)
    return pickle.dumps(data)

def unpack_data(data):
    filepaths = pickle.loads(data)
    return filepaths