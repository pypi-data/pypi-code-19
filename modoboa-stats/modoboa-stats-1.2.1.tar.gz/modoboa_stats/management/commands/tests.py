import os
import random

from dateutil import relativedelta
import rrdtool

from django.utils import timezone


def _create_new_accounts_rrd_file(fname, start):
    """Create RRD file."""
    step = 3600
    ds_name = "new_accounts"
    params = ["DS:{}:ABSOLUTE:{}:0:U".format(ds_name, step * 2)]
    params += [
        "RRA:AVERAGE:0.5:1:48",     # 48 hours with a 1h granularity
        "RRA:AVERAGE:0.5:24:31",    # 31 days with a 1d granularity
        "RRA:AVERAGE:0.5:168:52",   # 52 weeks with a 1w granularity
        "RRA:AVERAGE:0.5:5208:24",  # 24 months with a 1m granularity
    ]
    rrdtool.create(
        str(fname), "--start", str(start), "--step", str(step),
        *params
    )


def make_random_samples(start, end):
    db_path = "new_accounts.rrd"
    if os.path.exists(db_path):
        os.unlink(db_path)
    data = []
    hour = start
    while hour < end:
        next_hour = hour + relativedelta(hours=1)
        sample = random.randint(1, 20)
        print "Sample: {}".format(sample)
        data.append("{}:{}".format(
            int(next_hour.strftime("%s")), sample * 60))
        hour = next_hour
    if not os.path.exists(db_path):
        _create_new_accounts_rrd_file(
            db_path, int(start.strftime("%s")))
    rrdtool.update(str(db_path), *data)


if __name__ == "__main__":
    end = timezone.now().replace(minute=0, second=0, microsecond=0)
    start = end - relativedelta(years=1)
    make_random_samples(start, end)
