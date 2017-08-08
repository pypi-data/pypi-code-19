from aws_xray_sdk.core.models.trace_header import TraceHeader


TRACE_HEADER = 'X-Amzn-Trace-Id'


def inject_trace_header(headers, entity):
    """
    Extract trace id, entity id and sampling decision
    from the input entity and inject these information
    to headers.

    :param dict headers: http headers to inject
    :param Entity entity: trace entity that the trace header
        value generated from.
    """
    if not entity:
        return

    to_insert = TraceHeader(
        root=entity.trace_id,
        parent=entity.id,
        sampled=entity.sampled,
    )

    value = to_insert.to_header_str()

    headers[TRACE_HEADER] = value
