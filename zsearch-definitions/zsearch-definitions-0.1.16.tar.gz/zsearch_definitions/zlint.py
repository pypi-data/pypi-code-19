import sys
import zsearch_definitions.zlint_pb2

class LintResultStatus(object):

    _by_pretty_name = {}
    _by_name = {}
    _by_value = {}

    def __init__(self, value, name, pretty_name):
        self.value, self.name, self.pretty_name = value, name, pretty_name

    @classmethod
    def from_value(cls, value):
        return cls._by_value[value]

    @classmethod
    def from_name(cls, name):
        return cls._by_name[name]

    @classmethod
    def from_pretty_name(cls, name):
        return cls._by_pretty_name[name]

    def __hash__(self):
        return self.value.__hash__()

    def __cmp__(self, other):
        return self.value.__cmp__(other.value)


for _spid in zsearch_definitions.zlint_pb2.LintResultStatus.values():
    enum_name = zsearch_definitions.zlint_pb2.LintResultStatus.Name(_spid)
    simple_name = enum_name[len("LINT_RESULT_"):]
    pretty_name = simple_name.lower()
    object_ = LintResultStatus(_spid, enum_name, pretty_name)
    LintResultStatus._by_name[enum_name] = object_
    LintResultStatus._by_value[_spid] = object_
    LintResultStatus._by_pretty_name[pretty_name] = object_
    setattr(LintResultStatus, simple_name, object_)


