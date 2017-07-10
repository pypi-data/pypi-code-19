from datetime import datetime

from dateutil import parser as dt_parser
import pytz

def pretty_date(date_str):
  date = str_to_utc_datetime(date_str)
  return date.strftime('%X %x UTC')


def str_start_to_str_runtime(started):
  return get_duration_string(started, truncate=True)


def str_to_utc_datetime(date_str):
  date = dt_parser.parse(date_str)
  return date.replace(tzinfo=None)


def get_duration_string(started, stopped=None, truncate=False):
  if not started:
    return 'Not started'

  if stopped:
    end_date = str_to_utc_datetime(stopped)
  else:
    end_date = datetime.utcnow()

  start_date = str_to_utc_datetime(started)
  duration = (end_date - start_date).total_seconds()

  m, s = divmod(duration, 60)
  h, m = divmod(int(m), 60)
  d, h = divmod(h, 24)

  if truncate:
    duration_str = '{} seconds'.format(int(s))
  else:
    duration_str = '{0:.3f} seconds'.format(s)

  if m:
    m_str = str(m) + (' minutes' if m > 1 else ' minute')
    duration_str = m_str if truncate else m_str + ' ' + duration_str
  if h:
    h_str = str(h) + (' hours' if h > 1 else ' hour')
    duration_str = h_str if truncate else h_str + ' ' + duration_str
  if d:
    d_str = str(d) + (' days' if d > 1 else ' day')
    duration_str = d_str if truncate else d_str + ' ' + duration_str

  return duration_str
