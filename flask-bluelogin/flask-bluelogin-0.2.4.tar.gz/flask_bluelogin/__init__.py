#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Module flask_bluelogin
"""

__version_info__ = (0, 2, 4)
__version__ = '.'.join([str(val) for val in __version_info__])

__namepkg__ = "flask-bluelogin"
__desc__ = "Flask BlueLogin module"
__urlpkg__ = "https://github.com/fraoustin/flask-bluelogin.git"
__entry_points__ = {}

from flask_bluelogin.main import BlueLogin
from flask_bluelogin.models.user import User
from flask_bluelogin.models.users import Users
from flask_bluelogin.util import check_login

