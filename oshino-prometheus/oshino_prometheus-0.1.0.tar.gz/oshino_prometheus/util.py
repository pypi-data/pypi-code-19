import re

METRIC_PATTERN = re.compile("""
                             (?P<metric_key>\w+)
                            (\{(?P<meta>(\w|[.,\"=])+)\})?\s
                            (?P<metric_value>(\d|[.])+)
                    """, re.X)

META_PATTERN = re.compile("(?P<meta_key>(\w+)=\"(?P<meta_value>(\w|[.])+)\",?)*")


def parse_prometheus_metrics(raw):
    metrics = raw.split("\n")
    for metric in metrics:
        if metric.startswith("#"):  # This is comment
            continue

        metric_parsed = METRIC_PATTERN.match(metric)
        if metric_parsed is None:
            continue

        key = metric_parsed.group("metric_key")
        val = float(metric_parsed.group("metric_value"))

        def build_meta(raw):
            return raw[1], raw[2]

        meta_group = metric_parsed.group("meta")

        if meta_group is not None:
            meta_parsed = dict(map(build_meta,
                                   META_PATTERN.findall(meta_group)))
        else:
            meta_parsed = {}
        yield key, (val, meta_parsed,)
