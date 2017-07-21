class Foo(object):
    @classmethod
    def build(cls) -> 'Foo':
        pass

    def __eq__(self, other: 'Foo') -> bool:
        pass

    def method_with_mixed_annotations(self, other: 'Foo', flag: bool) -> bool:
        pass
