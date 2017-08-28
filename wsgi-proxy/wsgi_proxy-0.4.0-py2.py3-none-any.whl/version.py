""":mod:`wsgi_proxy.version` --- Version data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

"""

#: (:class:`str`) The version string e.g. ``'1.2.3'``.
VERSION = '0.4.0'

#: (:class:`tuple`) The triple of version numbers e.g. ``(1, 2, 3)``.
VERSION_INFO = tuple(map(int, VERSION.split('.')))


if __name__ == '__main__':
    print(VERSION)
