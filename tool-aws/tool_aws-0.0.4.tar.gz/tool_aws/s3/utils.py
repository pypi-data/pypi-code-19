import math
from textwrap import dedent


"""
Function that yields successive n-sized chunks from l.
"""


def chunks(l, n):
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


"""
Function that returns how many keys should be deleted at a time per process.
"""


def getMaxChunkSize(nbProc, nbKeys, maxChunkSize=1000):
    chunkSize = float(nbKeys) / float(nbProc)
    chunkSize = 1 if chunkSize < 1 and chunkSize > 0 else math.floor(chunkSize)
    return int(min(chunkSize, maxChunkSize))


"""
Function that returns keys given a bucket object and prefix.
"""


def getKeysFromS3(s3Bucket, prefix, maxKeys):
    return [{'Key': i.key}
            for i in s3Bucket.objects.filter(Prefix=prefix).limit(maxKeys)]


class S3Keys:
    """
    This class is used to generate chunks of keys, based on prefix key.
    """

    def __init__(self, s3Bucket, prefix, chunkSize=1, maxKeys=32000):
        self._prefix = prefix
        self._chunkSize = chunkSize
        self._keys = getKeysFromS3(s3Bucket, prefix, maxKeys)
        self._nbKeys = len(self._keys)
        self._chunkedKeys = chunks(self._keys, self._chunkSize)
        self._bucketName = s3Bucket.name
        self._maxKeys = maxKeys

    def __str__(self):
        return dedent("""\\n
            Number of keys: %d
            Chunk size    : %d
            Prefix        : %s
            Bucket name   : %s
            """ % (self._nbKeys, self._chunkSize,
                   self._prefix, self._bucketName))

    def __iter__(self):
        for cKeys in self._chunkedKeys:
            yield {'Objects': cKeys, 'Quiet': True}

    def __len__(self):
        return self._nbKeys

    def chunk(self, chunkSize):
        self._chunkSize = chunkSize
        self._chunkedKeys = chunks(self._keys, self._chunkSize)

    @property
    def prefix(self):
        return self._prefix

    @property
    def chunkedKeys(self):
        return self._chunkedKeys

    @property
    def chunkSize(self):
        return self._chunkSize

    @property
    def maxKeys(self):
        return self._maxKeys
