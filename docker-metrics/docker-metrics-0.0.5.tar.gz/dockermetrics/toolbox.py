import logging

logger = logging.getLogger(__name__)


def get_data_single(filePath):
    try:
        with open(filePath) as f:
            data = f.read().strip()
            if data.isdigit():
                data = int(data)
            return data, 0
    except Exception as e:
        errorMSG = 'Error accessing sysfs file {}: {}'.format(filePath, e)
        logger.exception(errorMSG)
        return errorMSG, 1


def get_data_multi(filePath, items):
    try:
        data = {}
        with open(filePath) as f:
            for line in f:
                key, val = line.strip().split()
                if val.isdigit():
                    val = int(val)
                if key in items:
                    data[key] = (val, 0)

        for item in items:
            if item not in data:
                data[item] = ('Unknown key', 1)

        return data
    except Exception as e:
        errorMSG = 'Error accessing sysfs file {}: {}'.format(filePath, e)
        logger.exception(errorMSG)
        data = {}
        for item in items:
            data[item] = (errorMSG, 1)
        return data


def get_data_selective(filePath, keyIndex=1, valIndex=2, items={}):
    try:
        data = {}
        with open(filePath) as f:
            for line in f:
                chunks = line.strip().split(' ')
                if len(chunks) >= (valIndex + 1) and chunks[keyIndex] in items:
                    data[chunks[keyIndex]] = (chunks[valIndex], 0)

        for item in items:
            if item not in data:
                data[item] = ('Unknown key', 1)

        return data
    except Exception as e:
        errorMSG = 'Error accessing sysfs file {}: {}'.format(filePath, e)
        logger.exception(errorMSG)
        data = {}
        for item in items:
            data[item] = (errorMSG, 1)
        return data
