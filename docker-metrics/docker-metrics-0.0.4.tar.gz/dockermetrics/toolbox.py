import logging

logger = logging.getLogger(__name__)


def get_data_single(filePath):
    try:
        with open(filePath) as f:
            data = f.read().strip()
            if data.isdigit():
                data = int(data)
            return data
    except Exception:
        logger.exception(u'Error accessing sysfs file')
        raise


def get_data_multi(filePath):
    try:
        ret = {}
        with open(filePath) as f:
            for line in f:
                key, val = line.strip().split()
                if val.isdigit():
                    val = int(val)
                ret[key] = val
        return ret
    except Exception:
        logger.exception(u'Error accessing sysfs file')
        raise


def get_data_selective(filePath, keyIndex=1, valIndex=2):
    try:
        ret = {}
        with open(filePath) as f:
            for line in f:
                chunks = line.strip().split(' ')
                if len(chunks) >= (valIndex + 1):
                    ret[chunks[keyIndex]] = chunks[valIndex]
        return ret
    except Exception:
        logger.exception(u'Error accessing sysfs file')
        raise
