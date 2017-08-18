from setuptools.dist import Distribution

class BinaryDistribution(Distribution):
    def is_pure(self):
        return False
