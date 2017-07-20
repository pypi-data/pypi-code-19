from datetime import datetime
import random
from unix_dates import UnixDate, UnixTimeDelta
import itculate_sdk as itsdk

LAMBDA_APPROXIMATE_PRICE_PER_MS = 0.000002396 / 100.0


class ConnectionsDataType(itsdk.CountDataType):
    pass


class ConnectionsPercentDataType(itsdk.PercentDataType):
    default_importance = itsdk.Importance.KPI_SYSTEM + 20


def common_document(vertices):
    common_document = None
    for vertex in vertices:
        if common_document:
            common_document = intersect_dicts(common_document, vertex)
        else:
            # remove the "_" attributes
            common_document = intersect_dicts(vertex, vertex)
    return common_document


def intersect_dicts(dict1, dict2):
    result = {}
    for k in dict1.viewkeys() & dict2.viewkeys():
        if k[0] == "_":
            continue

        v1 = dict1[k]
        v2 = dict2[k]
        if v1 and v2:
            if isinstance(v1, dict) and isinstance(v2, dict):
                sub_intersect = intersect_dicts(v1, v2)
                if sub_intersect:
                    result[k] = sub_intersect
            elif v1 == v2:
                result[k] = v1
    return result


def mockup_samples(itsdk, vertices,
                   feel_pain_vertices=None,
                   cause_pain_vertices=None,
                   contention_vertices=None,
                   message=None,
                   vertex_unhealthy=None,
                   rds_connection_utilization_vertices=None,
                   hour_of_event=14):
    """

    :type itsdk: itculate_sdk
    :type vertices: list[itculate_sdk.Vertex]
    :type feel_pain_vertices: list[itculate_sdk.Vertex]
    :type cause_pain_vertices: list[itculate_sdk.Vertex]
    :type contention_vertices: list[itculate_sdk.Vertex]
    :return:
    """
    end_time = UnixDate.now()
    start_time = end_time - UnixTimeDelta.calc(hours=48)

    now_less_24_hours = end_time - UnixTimeDelta.calc(hours=24)

    feel_pain_vertices_keys = {v.first_key for v in feel_pain_vertices} if feel_pain_vertices else {}
    cause_pain_vertices_keys = {v.first_key for v in cause_pain_vertices} if cause_pain_vertices else {}
    contention_vertices_keys = {v.first_key for v in contention_vertices} if contention_vertices else {}
    rds_connection_utilization_vertices_keys = {v.first_key for v in
                                                rds_connection_utilization_vertices} if rds_connection_utilization_vertices else {}

    event_timestamp = None

    for vertex in vertices:

        instance_count = 8

        connections = 88
        connections_percent = connections / 256.0
        rds_connection_utilization_started = False

        for timestamp in range(int(start_time), int(end_time), 15):

            date = datetime.fromtimestamp(timestamp=timestamp)

            hour = date.hour
            factor = max(1, (hour - 7) if hour < 13 else (21 - hour))

            invocations = random.randint(100, 200) + factor * random.randint(50, 80)
            duration = random.randint(91, 111)
            cpu_utilization = 0.1 * factor * random.random()
            memory_utilization = 5 + 2 * random.random()
            network_utilization = factor * random.random() / 20

            latency = max(1, int(random.randint(0, 10 * factor) + 10 * factor * random.random()))
            error_rate_1 = (factor + random.randint(1, 5)) / 100.0
            error_rate_2 = (factor + random.randint(1, 5)) / 100.0
            cache_miss = min(1.0, latency / 200.0)
            queue_io = random.randint(0, 2)

            price = duration * invocations * LAMBDA_APPROXIMATE_PRICE_PER_MS

            if hour == hour_of_event and timestamp > now_less_24_hours:
                event_timestamp = event_timestamp if event_timestamp else timestamp
                if vertex.first_key in feel_pain_vertices_keys:
                    latency = latency + random.randint(1000, 1200)
                    error_rate_1 = error_rate_1 * random.randint(2, 4)
                    error_rate_2 = 0
                    cpu_utilization = random.randint(8, 30) / 100.0
                    invocations *= 0.38
                elif vertex.first_key in cause_pain_vertices_keys:
                    cpu_utilization = random.randint(80, 99) / 100.0
                    network_utilization *= 2
                    invocations = invocations * random.randint(3, 5)
                    latency /= 3.0
                    cache_miss /= 5.0
                    error_rate_2 = 0
                elif vertex.first_key in contention_vertices_keys:
                    latency = latency + random.randint(290, 450)
                    cpu_utilization = random.randint(80, 99) / 100.0
                    network_utilization *= 2.3
                    queue_io = queue_io + random.randint(6, 10)

            if (hour == hour_of_event or rds_connection_utilization_started) and timestamp > now_less_24_hours:
                if vertex.first_key in rds_connection_utilization_vertices_keys:
                    rds_connection_utilization_started = True
                    connections = 228
                    connections_percent = connections / 256.0
                    instance_count = 24
                    cpu_utilization *= 1.3

            if vertex.type == "AWS_Lambda":
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations",
                                 value=itsdk.CountDataType.value(value=invocations, importance=1))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="duration",
                                 value=itsdk.DurationDataType.value(value=duration, importance=2))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="invocations-error-percent",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_1, importance=3))

                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="approximate-price-price",
                                 value=itsdk.PricePerPeriodDataType.value(value=price, importance=4))
            if vertex.type in ("AWS_RDS", "AWS_Aurora", "AWS_DynamoDB", "Service",
                               "AWS_Auto_Scaling_Group", "AWS_Instance", "AWS_Redshift",
                               "AWS_Memcached", "AWS_Redis", "AWS_ELB", "AWS_ALB"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="total-latency",
                                 value=itsdk.LatencyDataType.value(value=latency, importance=1))
            if vertex.type in ("AWS_RDS", "AWS_Aurora", "AWS_DynamoDB", "Service",
                               "AWS_Auto_Scaling_Group", "AWS_Instance", "AWS_Redshift",
                               "AWS_Memcached", "AWS_Redis",):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="cpu-utilization",
                                 value=itsdk.CPUPercentDataType.value(value=cpu_utilization, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="queue-iops",
                                 value=itsdk.QueueSizeDataType.value(value=queue_io, importance=3))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="memory-utilization",
                                 value=itsdk.MemoryPercentDataType.value(value=memory_utilization, visible=False))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="network-utilization",
                                 value=itsdk.NetworkPercentDataType.value(value=network_utilization, visible=False))
            if vertex.type in ("AWS_RDS", "AWS_Aurora"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="connections",
                                 value=ConnectionsDataType.value(value=connections, visible=False))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="connections-percent",
                                 value=ConnectionsPercentDataType.value(value=connections_percent, visible=False))
            if vertex.type in ("AWS_Auto_Scaling_Group", "Service"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="instance-count",
                                 value=itsdk.ObjectCountDataType.value(value=instance_count, visible=True))
            if vertex.type in ("AWS_Redshift", "AWS_Memcached", "AWS_Redis"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="cache-miss",
                                 value=itsdk.PercentDataType.value(value=cache_miss, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="total-commands",
                                 value=itsdk.RequestCountDataType.value(value=invocations, importance=3))
            if vertex.type in ("AWS_ELB", "AWS_ALB"):
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="request",
                                 value=itsdk.RequestCountDataType.value(value=invocations, importance=2))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="http-5XX-error-rate",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_1, importance=3))
                itsdk.add_sample(vertex=vertex,
                                 timestamp=timestamp,
                                 counter="http-4XX-error-rate",
                                 value=itsdk.ErrorPercentDataType.value(value=error_rate_2, visible=False))

        print "Flush timeseries for {}".format(vertex)
        itsdk.flush_all()

    if vertex_unhealthy and message:
        itsdk.vertex_unhealthy(collector_id="mockup_util",
                               vertex=vertex_unhealthy,
                               message=message,
                               timestamp=event_timestamp)
        itsdk.flush_all()
