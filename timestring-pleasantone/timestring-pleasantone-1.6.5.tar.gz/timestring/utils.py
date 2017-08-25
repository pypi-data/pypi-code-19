import pytz
from datetime import datetime

def get_timezone_time(tz):
    source_time = datetime.now(tz)
    return source_time