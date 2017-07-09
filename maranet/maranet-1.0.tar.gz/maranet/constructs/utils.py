from __future__ import print_function
import re
import datetime
from maranet.utils.checksum import make_cs_bigendian
from construct import (
    Container,
    Array,
    Byte,
    UBInt8,
)
from structs import MaraFrame
import jinja2


def ints2buffer(hexstr):
    '''Converts ints to buffer'''
    parts = [chr(an_int) for an_int in hexstr]
    return ''.join(parts)


def hexstr2buffer(a_str):
    '''
    "FE  01" => '\xFE\x01'
    '''
    a_str = a_str.strip().replace('\n', ' ')
    a_list = [chr(int(bytestr, 16)) for bytestr in re.split('[:\s]', a_str) if len(bytestr)]
    return ''.join(a_list)


def any2buffer(data):
    if isinstance(data, list):
        return ints2buffer(data)
    elif isinstance(data, basestring):
        return hexstr2buffer(data)
    raise Exception("%s can't be converted to string buffer")


def upperhexstr(buff):
    """Buffer -> Upper Human Readable Hex String"""
    return ' '.join([("%.2x" % ord(c)).upper() for c in buff])


def dtime2dict(dtime=None):
    '''
    Converts a datetime.datetime instance into
    a dictionary suitable for ENERGY event
    timestamp
    '''
    if not dtime:
        dtime = datetime.now()
    d = {}
    d['year'] = dtime.year % 100
    d['month'] = dtime.month
    d['day'] = dtime.day
    d['hour'] = dtime.hour
    d['minute'] = dtime.minute
    d['second'] = dtime.second
    # Ticks de cristal que va de 0 a 32K-1 en un segundo
    d['subsec'] = float(dtime.microsecond) / 1000000
    return d


def build_frame(obj, subcon=MaraFrame):
    '''Generates a mara frame, with checksum and qty'''
    stream = subcon.build(obj)
    data = "".join([
                    stream[0],
                    UBInt8('qty').build(len(stream)),
                    stream[2:-2],
                    ])
    cs = make_cs_bigendian(data)
    cs_str = Array(2, Byte('cs')).build(cs)
    return "".join((data, cs_str))


def parse_frame(buff, as_hex_string=False):
    if as_hex_string:
        buff = hexstr2buffer(buff)
    data = MaraFrame.parse(buff)
    return data

frame_template = Template("""\
{% if show_header %}\
    SOF: {{ d.sof }}
    QTY: {{ d.length }}
    DST: {{ d.dest }}
    SRC: {{ d.source }}
    SEQ: {{ d.sequence }}
    CMD: {{ d.command }}
{% endif %}\
{% if p.payload_10 %}\
    CANVARSYS:  {{p.canvarsys}}, Valores de word de 16: {{ p.canvarsys / 2 }}
    VARSYS:     {{p.varsys}}
    CANDIS:     {{p.candis}}, Valores de word de 16: {{p.candis / 2}}
    DIS:        {{p.dis}}
    CANAIS:     {{p.candis}}, Valores de word de 16: {{ p.canais / 2}}
    AIS:        {{p.ais}}
    CANEVS:     {{p.canevs}}, Elementos de 10 bytes {{p.canevs / 10}}
    {% for ev in p.event %}\
    {% if event.type == "DIGITAL" %}\
    {% elif event.type == "ENERGY" %}\
    {% endif %}\
    {% endfor %}\
{% endfor %}\
{% if show_bcc %}\
    BCC: {{ d.bcc }}
{% endif %}\
""")

def format_frame(buff, as_hex_string=False, show_header=True, show_bcc=True):
    """
    Formats a frame for pretty printing. Useful for debugging.
    Uses Jinja2
    """
    # TODO: Check if needs to be adapted for upcoming changes in Mara protocol
    if isinstance(buff, Container):
        d = buff
    else:
        d = parse_frame(buff, as_hex_string)
    if show_header:
        print("SOF:", d.sof)
        print("QTY:", d.length)
        print("DST:", d.dest)
        print("SRC:", d.source)
        print("SEQ:", d.sequence)
        print("CMD:", d.command)
    # Payload
    if d.payload_10:
        p = d.payload_10
        print("%12s" % "CANVARSYS:", p.canvarsys, "%d valores de word de 16" % (p.canvarsys / 2))
        print("%12s" % "VARSYS:", p.varsys)
        print("%12s" % "CANDIS:", p.candis, "%d valores de word de 16" % (p.candis / 2))
        print("%12s" % "DIS:", p.dis)
        print("%12s" % "CANAIS:", p.candis, "%d valores de word de 16" % (p.canais / 2))
        print("%12s" % "AIS:", p.ais)
        # Eventos
        print "%12s" % "CANEVS:", p.canevs, "%d cada evento ocupa 10 bytes" % (p.canevs / 10)
        for ev in p.event:
            if ev.evtype == "DIGITAL":
                print '\t',
                print "DIGITAL",
                print "Q:", ev.q,
                print "ADDR485", ev.addr485,
                print "BIT: %2d" % ev.bit,
                print "PORT:", ev.port,
                print "STATUS:", ev.status,
                print "%d/%d/%d %2d:%.2d:%2.2f" % (ev.year + 2000, ev.month, ev.day, ev.hour,
                                                   ev.minute, ev.second + ev.fraction)
                # print "%.2f" % ev.subsec

            elif ev.evtype == "ENERGY":
                print "\t",
                print "ENERGY Q: %d" % ev.q,
                print "ADDR485: %d" % ev.q, ev.addr485,
                print "CHANNEL: %d" % ev.channel,
                print "%d/%d/%d %2d:%.2d:%.2d" % (ev.year + 2000, ev.month, ev.day, ev.hour, ev.minute, ev.second),
                print "Value: %d Q: %d" % (ev.value.val, ev.value.q)
            else:
                print "Tipo de evento no reconocido"

    if show_bcc:
        print "BCC:", d.bcc
