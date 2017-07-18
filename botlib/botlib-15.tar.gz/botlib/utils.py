# LICENSE
#
# This file is released in the Public Domain.
#
# In case of copyright claims you can use this license 
# to prove that intention is to have no copyright on this work and
# consider it to be in the Publc Domain.
#
# Bart Thate
# Heerhugowaard
# The Netherlands

""" lib local helper functions. """

from .error import ENODATE
from .trace import get_exception
from .static import *

import html.parser
import rlcompleter
import datetime
import readline
import optparse
import _thread
import termios
import os.path
import hashlib
import logging
import random
import urllib
import urllib.request
import atexit
import botlib
import time
import stat
import json
import sys
import re
import os 

def high(target, file_name):
    highest = 0
    for i in os.listdir(target):
        if file_name in i:
            try: seqnr = i.split('.')[-1]
            except IndexError: continue  
            try:
                if int(seqnr) > highest: highest = int(seqnr)
            except ValueError: pass
    return highest

def highest(target, filename):
    nr = high(target, filename)
    return "%s.%s" % (filename, nr+1)

def locatedir(path, match=""):
    for root, dirs, files in os.walk(path):
        for d in dirs:
            if root == path:
                continue
            if match and match not in d:
                continue
            yield root

def copydir(orig, dest):
    for root, dirs, files in os.walk(orig):
        for d in dirs:
            if root == path:
                continue
            nr = copydir(dir, os.path.join(dest, d))
            counter = 0
            for fn in files:
                shutil.copy(os.path.join(root, d, fn), os.path.join(dest, fn))
                yield fn

def locked(func, *args, **kwargs):

    lock = _thread.allocate_lock()

    def lockedfunc(*args, **kwargs):
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc

def smooth(obj):
    if type(obj) not in basic_types:
        return repr(obj)
    return obj

def make_signature(object):
    data = json.dumps(object, indent=4, ensure_ascii=True, sort_keys=True)
    return str(hashlib.sha1(bytes(str(data), "utf-8")).hexdigest())

def verify_signature(object, signature):
    signature2 = make_signature(object)
    return signature2 == signature

def split_txt(txt, l=375):
    z = ""
    txt = str(txt)
    for t in txt.split("\n"):
        if len(t) < l: 
            yield t
        else:
            for y in t.split():
                if len(y) + len(z) < l:
                    z += " " + y
                    continue
                yield z.strip()
                z = ""
    if z:
        yield z.strip()

def cdir(path):
    res = "" 
    for p in path.split(os.sep):
        res += "%s%s" % (p, os.sep)
        padje = os.path.abspath(os.path.normpath(res))
        try:
            os.mkdir(padje)
        except (IsADirectoryError, NotADirectoryError, FileExistsError):
            pass
        except OSError as ex:
            logging.error(get_exception())
    return True

def get_url(url, **kwargs):
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url, headers={"User-Agent": useragent()})
    resp = urllib.request.urlopen(req)
    data = resp.read()
    logging.info("! %s %s %s" % (resp.status, resp.reason, url))
    return data

def useragent():
    return 'Mozilla/5.0 (X11; Linux x86_64) BOTLIB %s +https://bitbucket.org/bthate/botlib)' % botlib.__version__

def unescape(text):
    return html.parser.HTMLParser().unescape(text)

def strip_html(text):
    if text.startswith("http"):
        return text
    import bs4
    soup = bs4.BeautifulSoup(text, "lxml")
    res = ""
    for chunk in soup.findAll(text=True):
        if isinstance(chunk, bs4.CData): res += str(chunk.content[0]) + " "
        else: res += str(chunk) + " "
    return res

def locked(func, *args, **kwargs):

    lock = _thread.allocate_lock()

    def lockedfunc(*args, **kwargs):
        lock.acquire()
        res = None
        try:
            res = func(*args, **kwargs)
        finally:
            try:
                lock.release()
            except:
                pass
        return res
    return lockedfunc

def stripped(jid):
    try:
        return str(jid).split("/")[0]
    except:
        return str(jid)

def userhost(u):
    try:
        return str(u).split("!")[-1]
    except:
        return str(u)

def parse_cli(*args, **kwargs):
    from .object import Config
    from .template import opts_defs
    opts, arguments = make_opts(opts_defs)
    cfg = Config()
    cfg.template("kernel")
    cfg.args = arguments
    cfg.merge(vars(opts))
    return cfg

def termsetup(fd):
    old = termios.tcgetattr(fd)
    return old

def termreset(fd, old):
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

class Completer(rlcompleter.Completer):

    def __init__(self, options):
        super().__init__()
        self.options = options
 
    def complete(self, text, state):
        if state == 0:
            if text:
                self.matches = [s for s in self.options if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None

def set_completer(optionlist):
    import readline
    readline.parse_and_bind("tab: complete")
    completer = Completer(optionlist)
    readline.set_completer(completer.complete)
    atexit.register(lambda: readline.set_completer(None))

def enable_history():
    if not os.path.exists(histfile):
        d, f = os.path.split(histfile)
        cdir(d)
        touch(histfile)
    readline.read_history_file(histfile)
    atexit.register(close_history)

def close_history():
    readline.write_history_file(histfile)

def reset():
    close_history()
    if "old" in resume:
        termreset(resume["fd"], resume["old"])
    
def startup():
    global resume
    resume["fd"] = sys.stdin.fileno()
    resume["old"] = termsetup(sys.stdin.fileno())
    atexit.register(reset)

def make_opts(options):
    import botlib
    parser = optparse.OptionParser(usage='usage: %prog [options]', version=str(botlib.__version__))
    for option in options:
        type, default, dest, help = option[2:]
        if "store" in type:
            try:
                parser.add_option(option[0], option[1], action=type, default=default, dest=dest, help=help)
            except Exception as ex: 
                logging.error("%s option %s" % (str(ex), option))
                continue
        else:
            try:
                parser.add_option(option[0], option[1], type=type, default=default, dest=dest, help=help)
            except Exception as ex:
                logging.error("^%s option %s" % (str(ex), option)) ; continue
    args = parser.parse_args()
    return args

def reboot():
    os.execl(sys.argv[0], *(sys.argv + ["-r", "-z"]))

def name(object):
    txt = repr(object)[1:-1]
    return fromstring(txt)

def fromstring(txt):
    if " object " in txt:
        txt = txt.split(" object ")[0]
    elif " at " in txt:
        txt = txt.split(" at ")[0]
    elif "bound method" in txt:
        txt = txt.split("bound method")[1].split()[0]
    if " of " in txt:
        t1, t2 = txt.split(" of ")
        txt = t2.split(".")[-1] + "." + t1.split(".")[-1]
    elif " from " in txt:
        txt = txt.split(" from ")[0].split()[1][1:-1]
    if "," in txt:
        txt = txt.split(",")[0]
    txt = txt.replace("<", "")
    txt = txt.replace("<function ", "")
    txt = txt.replace("function ", "")
    txt = txt.replace("<bound method ", "")
    txt = txt.replace("bound method ", "")
    return txt.strip()

def pname(object):
    return repr(object)

def sname(object):
    return tname(object).split(".")[-1]

def tname(object):
    return name(object).split("(")[-1]

def n(object):
    return str(object.__class__).split()[-1].split(".")[-1][:-2].lower()

def pathname(path):
    from .space import cfg
    d = cfg.workdir.split(os.sep)[-1]
    return d + path.split(cfg.workdir)[-1]

def fn_time(daystr):
    """ determine the time used in a BOTLIB filename. """
    daystr = daystr.replace("_", ":")
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.split(".")[0]
    try:
        t = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    except ValueError:
        t = 0
    return t

def now():
    """ turn a datetime string of the current time. """
    return str(datetime.datetime.now())

def rtime():
    """ return a filestamp usable in a filename. """
    return str(datetime.datetime.now()).replace(" ", os.sep)

def hms():
    """ return hour:minutes:seconds of toda=y. """
    return str(datetime.datetime.today()).split()[1].split(".")[0]

def day():
    """" return the current day. """
    return str(datetime.datetime.today()).split()[0]

def year():
    """ return the year we are living in. """
    return str(datetime.datetime.now().year)

def get_hour(daystr):
    """ get the hour from the string provided. """
    try:
        hmsre = re.search('(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hms = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search('(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hms = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hms

def get_time(txt):
    """ get time from a string containing day and/or hour. """
    try:
        target = get_day(txt)
    except ENODATE:
        target = to_day(day())
    hour =  get_hour(txt)
    if hour:
        target += hour
    return target

def parse_time(txt):
    """" parse a string for a time mentioned. also parse for a diff in seconds. """
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = get_day(txt)
        except ENODATE:
            target = to_day(day())
        hour =  get_hour(txt)
        if hour:
            target += hour
    return target

def extract_time(daystr):
    """ use standard time timeformats to extract a time from a string. """
    for format in year_formats:
        try:
            res = time.mktime(time.strptime(daystr, format))
        except:
            res = None
        if res:
            return res

def to_day(daystring):
    """ try to detect a time in a string. """
    previous = ""
    line = ""
    daystr = str(daystring)
    for word in daystring.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_time(line.strip())
        except ValueError:
            res = None
        if res:
            return res
        line = ""

def to_time(daystr):
    """
         convert time/date string to a unix timestamp

         example: 2016-08-29 16:34:23.837288
         example: Sat Jan 14 00:02:29 2017

    """
    daystr = str(daystr)
    daystr = daystr.split(".")[0]
    daystr = daystr.replace("GMT", "")
    daystr = daystr.replace("_", ":")
    daystr = " ".join([x.capitalize() for x in daystr.split() if not x[0] in ["+", "-"]])
    res = 0
    try:
        res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S"))
    except:
        pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a, %d %b %Y %H:%M:%S %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %d %b %H:%M:%S %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %b %d %H:%M:%S %Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%a %d %b %H:%M:%S %Y %z"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M:%S"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d %H:%M"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%Y-%m-%d"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d-%m-%Y"))
        except:
            pass
    if not res:
        try:
            res = time.mktime(time.strptime(daystr, "%d %m %Y"))
        except:
            pass
    if not res:
        raise ENODATE(daystr)
    return res

def file_time(timestamp):
    """ return a pseudo random time on today's start of the day. """
    return str(datetime.datetime.fromtimestamp(timestamp)).replace(" ", os.sep) + "." + str(random.randint(111111,999999))

def to_date(*args, **kwargs):
    """ convert to date. """
    if not args:
        return None
    date = args[0]
    if not date:
        return None
    date = date.replace("_", ":")
    res = date.split()
    ddd = ""
    try:
        if "+" in res[3]: 
            raise ValueError
        if "-" in res[3]:
            raise ValueError
        int(res[3])
        ddd = "{:4}-{:#02}-{:#02} {:6}".format(res[3], monthint[res[2]], int(res[1]), res[4])
    except (IndexError, KeyError, ValueError):
        try:
            if "+" in res[4]:
                raise ValueError
            if "-" in res[4]:
                raise ValueError
            int(res[4])
            ddd = "{:4}-{:#02}-{:02} {:6}".format(res[4], monthint[res[1]], int(res[2]), res[3])
        except (IndexError, KeyError, ValueError):
            try:
                ddd = "{:4}-{:#02}-{:02} {:6}".format(res[2], monthint[res[1]], int(res[0]), res[3])
            except (IndexError, KeyError):
                try:
                    ddd = "{:4}-{:#02}-{:02}".format(res[2], monthint[res[1]], int(res[0]))
                except (IndexError, KeyError):
                    try:
                        ddd = "{:4}-{:#02}".format(res[2], monthint[res[1]])
                    except (IndexError, KeyError):
                        try:
                            ddd = "{:4}".format(res[2])
                        except (IndexError, KeyError):
                            ddd = ""
    return ddd

def elapsed(seconds, short=True):
    """ return a string showing the elapsed days, hours, minutes, seconds. """
    txt = ""
    sub = str(seconds).split(".")[-1]
    nsec = float(seconds)
    year = 365*24*60*60
    week = 7*24*60*60
    day = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    days = int(nsec/day)
    nsec -= days*day
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    sec = nsec - minutes*minute
    if years:
        txt += "%sy" % years
    if weeks:
        days += weeks * 7
    if days:
        txt += "%sd" % days
    if years and short and txt:
        return txt
    if hours:
        txt += "%sh" % hours 
    if days and short and txt:
        return txt
    if minutes:
        txt += "%sm" % minutes
    if hours and short and txt:
        return txt
    if sec == 0:
        txt += "0s"
    elif sec < 1 or not short:
        txt += "%.3fs" % sec
    else:
        txt += "%ss" % int(sec)
    txt = txt.strip()
    return txt

def today():
    """" return the day of a filename. """
    t = rtime().split(".")[0]
    ttime = time.strptime(t, "%Y-%m-%d/%H:%M:%S")
    result = time.mktime(ttime)
    return result

def get_day(daystring):
    """ get the day from the string provided. """
    day = 0
    try:
        ymdre = re.search('(\d+)-(\d+)-(\d+)', daystring)
        if ymdre:
            (year, month, day) = ymdre.groups()
    except:
        try:
            ymre = re.search('(\d+)-(\d+)', daystring)
            if ymre:
                (year, month) = ymre.groups()
                day = 1
        except:
            raise ENODATE(daystring)
    if not day:
        raise ENODATE(daystring)
    day = int(day)
    month = int(month)
    year = int(year)
    date = "%s %s %s" % (day, bdmonths[month], year)
    return time.mktime(time.strptime(date, "%d %b %Y"))


def urled(object):
    """ return a url for the object so it can be fetched with the REST service. """
    from .space import cfg
    p = get_path(object)
    p = p.split(cfg.workdir)[-1]
    return "http://%s:%s%s" % (cfg.hostname or "localhost", cfg.port, p)

def root():
    """ return the root directory. """
    from .space import cfg
    path = cfg.workdir
    path = os.path.abspath(path)
    check_permissions(path)
    return path

def days(object):
    """ calculate the time passed since an object got logged. """
    t1 = time.time()
    #t2 = dated(object)
    t2 = timed(object)
    if t2:
        time_diff = float(t1 - t2)
        return elapsed(time_diff)

def dated(object):
    """ fetch the date from an object. """
    res = ""
    if "_container" in object:
        object = object._container
    if not res:
        res = getattr(object, "Date", None)
    if not res:
        res = getattr(object, "date", None)
    if not res:
        res = getattr(object, "published", None)
    if not res:
        res = getattr(object, "added", None)
    if not res:
        res = getattr(object, "saved", None)
    if not res:
        res = getattr(object, "timed", None)
    if not res:
        raise ENODATE(res)
    return res

def timed(object):
    """ calculated the time of an object. """
    try:
        return fn_time(object._container.path)
    except:
        try:
            return fn_time(rtime())
        except:
           pass
    try:
        date = dated(object._container)
    except (AttributeError, ENODATE):
        try:
           date = dated(object)
        except ENODATE:
           date = None
    if date:
        try: 
            return to_time(date)
        except ENODATE:
            pass

def get_path(object):
    """ Return the path used to store the object's json dump. """
    try:
        return object._container.path
    except:
        pass

def get_saved(object):
    """ return the saved attribue of an object. """
    p = ""
    if "_container" in object:
        p = getattr(object._container, "saved", "")
        if p:
            return p

def check_permissions(path, dirmask=dirmask, filemask=filemask):
    uid = os.getuid()
    gid = os.getgid()
    try:
        stats = os.stat(path)
    except FileNotFoundError:
        return
    except OSError:
        d, fn = os.path.split(path)
        cdir(d)
        stats = os.stat(d)
    if stats.st_uid != uid:
        os.chown(path, uid, gid)
    if os.path.isfile(path):
        mask = filemask
    else:
        mask = dirmask
    m = oct(stat.S_IMODE(stats.st_mode))
    if m != oct(mask):
        os.chmod(path, mask)

def touch(fname):
    try:
        fd = os.open(fname, os.O_RDONLY | os.O_CREAT)
        os.close(fd)
    except TypeError:
        pass
    except Exception as ex:
        logging.error(get_exception())
