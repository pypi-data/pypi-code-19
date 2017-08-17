"""
 # Copyright (c) 06 2016 | suryakencana
 # 6/13/16 nanang.ask@kubuskotak.com
 # This program is free software; you can redistribute it and/or
 # modify it under the terms of the GNU General Public License
 # as published by the Free Software Foundation; either version 2
 # of the License, or (at your option) any later version.
 #
 # This program is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with this program; if not, write to the Free Software
 # Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
 #  helper.py
"""
import datetime
import hashlib
import random
import time
from slugify import slugify
from baka_model.model import pubid
from baka_model.model.meta.base import Base
from baka_model.model.meta.schema import utcnow
from sqlalchemy import Column, Integer, FLOAT, Unicode, CHAR, event
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import synonym
from dateutil import tz


# for datetime utc convert to current timezone
def utc_tz(dt):
    try:
        if isinstance(dt, datetime.datetime):
            return dt.replace(tzinfo=tz.tzutc()).astimezone(tz.tzlocal())
    except ValueError:
        pass


def guid(*args):
    """
    Generates a universally unique ID.
    Any arguments only create more randomness.
    """
    t = float(time.time() * 1000)
    r = float(random.random()*10000000000000)

    a = random.random() * 10000000000000
    data = str(t) + ' ' + str(r) + ' ' + str(a) + ' ' + str(args)
    data = hashlib.md5(data.encode()).hexdigest()[:10]

    return data


class Followers(object):
    viewed = Column(Integer, default=0)
    rating = Column(FLOAT, default=0.0)
    votes = Column(Integer, default=0)
    # generate untuk posisi rank
    rank = Column(Integer, default=0)


class Slugger(object):

    _max_slug_length = 64
    _slug_is_unique = True

    _slug = Column('slug', Unicode(200), unique=_slug_is_unique)

    def _set_slug(self, name):
        self._slug = slugify(name, to_lower=True)

    def _get_slug(self):
        return self._slug

    """it's cool alias routed"""
    @declared_attr
    def slug(cls):
        return synonym('_slug', descriptor=property(cls._get_slug,
                                                    cls._set_slug))


class SurrogatePK(object):
    """A mixin that adds a surrogate integer 'primary key' column named
    ``id`` to any declarative-mapped class."""

    # id = Column(Integer, primary_key=True)
    id = Column(CHAR(10), primary_key=True, default=guid)
