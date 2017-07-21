# -*- coding: utf-8 -*-
import os
import re
import time
from math import sqrt

import sys

if sys.version_info[0] == 2:
    import ipaddr as ipaddress
    from ipaddr import IPAddress as ip_address
else:
    import ipaddress
    from ipaddress import ip_address


def get_client_ip(request):
    """Return IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    ip = False
    if x_forwarded_for:
        try:
            ip = ip_address(x_forwarded_for.split(',')[0])
        except ValueError:
            try:  # sometimes IP address in next index %-O
                ip = ip_address(x_forwarded_for.split(',')[1])
            except (ValueError, IndexError):
                ip = False
    if not ip:
        try:
            ip = ip_address(request.META.get('REMOTE_ADDR'))
        except ValueError:
            pass
    return ip


RUSSIAN_MAP = {
    u'а': 'a', u'б': 'b', u'в': 'v', u'г': 'g', u'д': 'd', u'е': 'e', u'ё': 'yo', u'ж': 'zh',
    u'з': 'z', u'и': 'i', u'й': 'j', u'к': 'k', u'л': 'l', u'м': 'm', u'н': 'n', u'о': 'o',
    u'п': 'p', u'р': 'r', u'с': 's', u'т': 't', u'у': 'u', u'ф': 'f', u'х': 'h', u'ц': 'c',
    u'ч': 'ch', u'ш': 'sh', u'щ': 'sh', u'ъ': '', u'ы': 'y', u'ь': '', u'э': 'e', u'ю': 'yu',
    u'я': 'ya',
    u'А': 'A', u'Б': 'B', u'В': 'V', u'Г': 'G', u'Д': 'D', u'Е': 'E', u'Ё': 'Yo', u'Ж': 'Zh',
    u'З': 'Z', u'И': 'I', u'Й': 'J', u'К': 'K', u'Л': 'L', u'М': 'M', u'Н': 'N', u'О': 'O',
    u'П': 'P', u'Р': 'R', u'С': 'S', u'Т': 'T', u'У': 'U', u'Ф': 'F', u'Х': 'H', u'Ц': 'C',
    u'Ч': 'Ch', u'Ш': 'Sh', u'Щ': 'Sh', u'Ъ': '', u'Ы': 'Y', u'Ь': '', u'Э': 'E', u'Ю': 'Yu',
    u'Я': 'Ya'
}


def _makeRegex():
    ALL_DOWNCODE_MAPS = {}
    ALL_DOWNCODE_MAPS.update(RUSSIAN_MAP)
    s = u"".join(ALL_DOWNCODE_MAPS.keys())
    regex = re.compile(u"[%s]|[^%s]+" % (s, s))

    return ALL_DOWNCODE_MAPS, regex


_MAPINGS = None
_regex = None


def downcode(s):
    """
    This function is 'downcode' the string pass in the parameter s. This is useful
    in cases we want the closest representation, of a multilingual string, in simple
    latin chars. The most probable use is before calling slugify.
    """
    global _MAPINGS, _regex

    if not _regex:
        _MAPINGS, _regex = _makeRegex()

    downcoded = ""
    for piece in _regex.findall(s):
        if _MAPINGS.has_key(piece):
            downcoded += _MAPINGS[piece]
        else:
            downcoded += piece
    return downcoded


def gen_url(size):
    """Generate url with given size"""

    import random
    import string
    alph = "%s%s_-" % (string.digits, string.ascii_letters)
    l = len(alph) - 1
    url = ''.join([random.choice(alph) for i in range(0, size)])
    return url


def get_page_range(paginator, page, page_links=15):
    """
    Generate page range
    """
    _PAGE_LINKS = page_links
    page_range = []
    if page < _PAGE_LINKS // 2:
        if len(paginator.page_range) > _PAGE_LINKS:
            page_range = [p for p in range(1, _PAGE_LINKS + 1)]
        else:
            page_range = paginator.page_range
    else:
        for p in paginator.page_range:
            if p < page:
                if page - p < (_PAGE_LINKS) // 2:
                    page_range.append(p)
            if p >= page:
                if p - page < (_PAGE_LINKS) // 2:
                    page_range.append(p)

        if len(page_range) > _PAGE_LINKS and page > (_PAGE_LINKS) // 2:
            page_range = page_range[:-1]
    return page_range


def page_range_from_list(pages, page, page_links=15):
    """
    Generate page range from list of pages, like [1,2,3]...
    """
    half_pl = page_links // 2
    page_range = []
    if half_pl * 2 - 1 > page:
        if len(pages) > page_links:
            page_range = [p for p in range(1, page_links + 1)]
        else:
            page_range = pages
    else:
        for p in pages:
            if p < page:
                if page - p < half_pl:
                    page_range.append(p)
            if p >= page:
                if p - page < half_pl:
                    page_range.append(p)

        if len(page_range) > page_links and page > half_pl:
            page_range = page_range[:-1]
    return page_range


def humanizeTimeDiff(timestamp=None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...

    from http://djangosnippets.org/snippets/412/

    """
    import datetime

    timeDiff = datetime.datetime.now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds / 3600
    minutes = timeDiff.seconds % 3600 / 60
    seconds = timeDiff.seconds % 3600 % 60
    months = days / 30
    years = days / 365
    sstr = u""
    tStr = u""
    # print "<<", years, months

    if years > 0:
        if str(years)[-1:] == u'1':
            tStr = u"год назад"
        elif str(years)[-1:] in [u'2', u'3', u'4', ] and str(years)[0] != u'1':
            tStr = u"года назад"
        else:
            tStr = u"лет назад"
        sstr = sstr + u"%s %s" % (years, tStr)
        return sstr

    elif months > 0:
        if str(months)[-1:] == u'1':
            tStr = u"месяц назад"
        elif str(months)[-1:] in [u'2', u'3', u'4', ] and str(months)[0] != u'1':
            tStr = u"месяца назад"
        else:
            tStr = u"месяцев назад"
        sstr = sstr + u"%s %s" % (months, tStr)
        return sstr

    elif days > 0:
        if str(days)[-1:] == u'1':
            tStr = u"день назад"
        elif str(days)[-1:] in [u'2', u'3', u'4', ] and str(days)[0] != u'1':
            tStr = u"дня назад"
        else:
            tStr = u"дней назад"
        sstr = sstr + u"%s %s" % (days, tStr)
        return sstr

    elif hours > 0:
        if hours == 1:
            tStr = u"час назад"
        elif str(hours)[-1:] in [u'2', u'3', u'4', ] and str(hours)[0] != u'1':
            tStr = u"часа назад"
        else:
            tStr = u"часов назад"
        sstr = sstr + u"%s %s" % (hours, tStr)
        return sstr
    elif minutes > 0:
        if minutes == 1:
            tStr = u"минуту назад"
        elif str(minutes)[-1:] in [u'2', u'3', u'4', ] and str(minutes)[0] != u'1':
            tStr = u"минуты назад"
        else:
            tStr = u"минут назад"
        sstr = sstr + u"%s %s" % (minutes, tStr)
        return sstr
    elif seconds > 0:
        if seconds == 1:
            tStr = u"секунду назад"
        elif str(seconds)[-1:] in [u'2', u'3', u'4', ] and str(seconds)[0] != u'1':
            tStr = u"секунды назад"
        else:
            tStr = u"секунд назад"
        sstr = sstr + u"%s %s" % (seconds, tStr)
        return sstr
    else:
        return u"Только что"


def wilson_score(sum_rating, n, votes_range=[0, 1]):
    """Wilson score using code from
    http://habrahabr.ru/company/darudar/blog/143188/

    sum_rating - sum of votes
    n - amount of votes
    """

    z = 1.64485
    v_min = min(votes_range)
    v_width = float(max(votes_range) - v_min)
    try:
        phat = (sum_rating - n * v_min) / v_width / float(n)
        rating = (phat + z * z / (2 * n) - z * sqrt(
            (phat * (1 - phat) + z * z / (4 * n)) / n)) / (1 + z * z / n)
    except ZeroDivisionError:
        return 0
    return rating * v_width + v_min


def inttomonth(i):
    months = ('', u'Января', u'Февраля', u'Марта', u'Апреля',
              u'Мая', u'Июня', u'Июля', u'Августа', u'Сентября',
              u'Октября', u'Ноября', u'Декабря',)
    return months[i]


def inttomontht(i):
    months = ('', u'Январе', u'Феврале', u'Марте', u'Апреле',
              u'Мае', u'Июне', u'Июле', u'Августе', u'Сентябре',
              u'Октябре', u'Ноябре', u'Декабре',)
    return months[i]


def inttomonthi(i):
    months = ('', u'Январь', u'Февраль', u'Март', u'Апрель',
              u'Май', u'Июнь', u'Июль', u'Август', u'Сентябрь',
              u'Октябрь', u'Ноябрь', u'Декабрь',)
    return months[i]


def monthtoint(m):
    months = ('', u'Января', u'Февраля', u'Марта', u'Апреля',
              u'Мая', u'Июня', u'Июля', u'Августа', u'Сентября',
              u'Октября', u'Ноября', u'Декабря',)
    return months.index(m)
