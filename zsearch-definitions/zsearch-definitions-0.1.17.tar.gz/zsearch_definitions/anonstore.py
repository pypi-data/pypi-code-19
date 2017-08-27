import sys
import zsearch_definitions.certificate_pb2
import zsearch_definitions.zlint_pb2


class ZProtobufEnum(object):

    def __init__(self, value, name, pretty_name):
        self.value = value
        self.name = name
        self.pretty_name = pretty_name

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


def make_enum(name, definition, prefix):

    class X(ZProtobufEnum):
        _by_pretty_name = {}
        _by_name = {}
        _by_value = {}

    X.__name__ = name
    for _spid in definition.values():
        enum_name = definition.Name(_spid)
        simple_name = enum_name[len(prefix) + 1:]
        pretty_name = simple_name.lower()
        object_ = X(_spid, enum_name, pretty_name)
        X._by_name[enum_name] = object_
        X._by_value[_spid] = object_
        X._by_pretty_name[pretty_name] = object_
        setattr(X, simple_name, object_)

    return X


CertificateSource = make_enum(
        "CertificateSource",
        zsearch_definitions.certificate_pb2.CertificateSource,
        "CERTIFICATE_SOURCE")

CTPushStatus = make_enum(
        "CTPushStatus",
        zsearch_definitions.ct_pb2.CTPushStatus,
        "CT_PUSH_STATUS")

CertificateParseStatus = make_enum(
        "CertificateParseStatus",
        zsearch_definitions.certificate_pb2.CertificateParseStatus,
        "CERTIFICATE_PARSE_STATUS")

CertificateType = make_enum(
        "CertificateType",
        zsearch_definitions.certificate_pb2.CertificateType,
        "CERTIFICATE_TYPE")

CertificateRevocationReason = make_enum(
        "CertificateRevocationReason",
        zsearch_definitions.certificate_pb2.CertificateRevocationReason,
        "CERTIFICATE_REVOCATION_REASON")

LintResultStatus = make_enum(
        "LintResultStatus",
        zsearch_definitions.zlint_pb2.LintResultStatus,
        "LINT_RESULT")

ZLintStatus = make_enum(
        "ZLintStatus",
        zsearch_definitions.zlint_pb2.ZLintStatus,
        "ZLINT_STATUS")

CTPushStatus = make_enum(
        "CTPushStatus",
        zsearch_definitions.ct_pb2.CTPushStatus,
        "CT_PUSH_STATUS")

CTServer = make_enum(
        "CTServer",
        zsearch_definitions.ct_pb2.CTServer,
        "CT_SERVER")
