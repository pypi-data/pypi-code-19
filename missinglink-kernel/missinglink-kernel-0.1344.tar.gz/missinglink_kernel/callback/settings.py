CUSTOM_METRICS_FORMAT = 'ml_custom_{}'


class HyperParamTypes(object):
    RUN = 'run'
    OPTIMIZER = 'optimizer'
    MODEL = 'model'
    CUSTOM = 'custom'


class EventTypes(object):
    TRAIN_BEGIN = 'TRAIN_BEGIN'
    TRAIN_END = 'TRAIN_END'
    EPOCH_BEGIN = 'EPOCH_BEGIN'
    EPOCH_END = 'EPOCH_END'
    EPOCH_UPDATE = 'EPOCH_UPDATE'
    BATCH_BEGIN = 'BATCH_BEGIN'
    BATCH_END = 'BATCH_END'
    BATCH_UPDATE = 'BATCH_UPDATE'
    TEST_BEGIN = 'TEST_BEGIN'
    TEST_END = 'TEST_END'
    TEST_ITERATION_END = 'TEST_ITERATION_END'
