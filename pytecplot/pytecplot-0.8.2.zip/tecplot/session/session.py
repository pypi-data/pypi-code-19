import atexit

from datetime import date

from ..tecutil import _tecutil_connector


@atexit.register  # Automatically call stop() when Python is unloaded
def stop():
    """Releases the |Tecplot License| and shuts down |Tecplot Engine|.

    This shuts down the |Tecplot Engine| and releases the |Tecplot License|.
    Call this function when your script is finished using |PyTecplot|.
    Calling this function is not required. If you do not call this function,
    it will be called automatically when your script exists. However, the
    |Tecplot License| will not be released until you call this function.

    Note that stop() may only be called once during the life of a Python
    session. If it has already been called, subsequent calls do nothing.

    See also: `tecplot.session.acquire_license()`,
    `tecplot.session.release_license()`.

    Example::

            >>> import tecplot
            >>> # Do useful things with pytecplot
            >>> tecplot.session.stop() # Shutdown tecplot and release license
    """
    _tecutil_connector.stop()


def acquire_license():
    """Attempts to acquire the |Tecplot License|

    Call this function to attempt to acquire a |Tecplot License|. If
    |Tecplot Engine| is not started, this function will start the
    |Tecplot Engine| before attempting to acquire a license.

    This function can be used to re-acquire a license that was released with
    `tecplot.session.release_license`.

    If the |Tecplot Engine| is currently running, and a
    |Tecplot License| has already been acquired, this function has no effect.

    Licenses may be acquired and released any number of times during the same
    Python session.

    Raises `TecplotLicenseError` if a valid license could not be acquired.

    .. note:: Warning emitted when close to expiration date.

        A warning is emitted using Python's built-in `warnings` module if you
        are within 30 days of your TecPLUS subscription expiration date. The message will look like this:

        .. code-block:: shell

            $ python
            Python 3.4.5 (default, Jun 27 2016, 13:24:59)
            [GCC 4.8.5 20150623 (Red Hat 4.8.5-4)] on linux
            Type "help", "copyright", "credits" or "license" for more information.
            >>> import tecplot
            >>> tecplot.session.acquire_license()
            /path/to/tecutil_connector.py:458: UserWarning:
            Your Tecplot software maintenance subscription
            (TecPLUS) will expire in **13 days**, after which you
            will no longer be able to use PyTecplot. Contact
            sales@tecplot.com to renew your TecPLUS subscription.

              warn(warning_msg)
            >>>

        These warnings can be suppressed by using the ``-W ignore`` option when
        invoking the python interpreter:

        .. code-block:: shell

            $ python -W ignore
            >>> import tecplot
            >>> tecplot.session.acquire_license()
            >>>

    See also: `tecplot.session.release_license()`

    Example::

        >>> import tecplot
        >>> # Do useful things
        >>> tecplot.session.release_license()
        >>> # Do time-consuming things not related to |PyTecplot|
        >>> tecplot.session.acquire_license()  # re-acquire the license
        >>> # Do useful |PyTecplot| related things.
    """
    _tecutil_connector.acquire_license()


def release_license():
    """Attempts to release the |Tecplot License|

    Call this to release a |Tecplot License|. Normally you do not need to call
    this function since `tecplot.session.stop()` will call it for you when your
    script exists and the Python interpreter is unloaded.

    This function can be used to release a license so that the license is
    available to other instances of |Tecplot 360|.

    If the |Tecplot License| has already been released, this function has
    no effect.

    Licenses may be acquired and released any number of times during the same
    Python session.

    See also: `tecplot.session.acquire_license()`

    Example usage::

        >>> import tecplot
        >>> # Do useful things
        >>> tecplot.session.release_license()
        >>> # Do time-consuming things not related to |PyTecplot|
        >>> tecplot.session.acquire_license()  # re-acquire the license
        >>> # Do useful |PyTecplot| related things.
    """
    _tecutil_connector.release_license()


def start_roaming(days):
    """Check out a roaming license.

    Parameters:
        days (`integer <int>`): Number of days to roam.

    This will acquire a PyTecplot license and then attempt to set it up for
    roaming. The maximum number of days one may roam is typically 90. This
    function can be called in an interactive terminal
    and will affect all subsequent uses of PyTecplot on the local machine.
    Do not forget to `release <tecplot.session.stop_roaming>`
    the roaming license to the server if you are finished roaming before the
    expiration date.

    See also: `tecplot.session.stop_roaming()`

    Example usage::

        >>> tecplot.session.start_roaming(10)
        You have successfully checked out a roaming license of
        PyTecplot. This will be valid for 10 days until
        midnight of 2017-01-15.
        >>> tecplot.session.stop_roaming()
        Your PyTecplot roaming license has been checked in.
    """
    _tecutil_connector.start_roaming(days)


def stop_roaming(force=False):
    """Check in (release) a roaming license.

    This will check in and make available to others on the network a license
    that you previously checked out for roaming.

    See also: `tecplot.session.start_roaming()`

    Example usage::

        >>> tecplot.session.stop_roaming()
        Your PyTecplot roaming license has been checked in.
    """
    _tecutil_connector.stop_roaming(force)


def license_expiration():
    """Expiration date of the current license.

    Returns: `datetime.date`

    Example usage::

        >>> print(tecplot.session.license_expiration())
        2017-12-31
    """
    expire = _tecutil_connector.license_expiration
    if isinstance(expire, date):
        return expire


def connect(host='localhost', port=7600):
    _tecutil_connector.connect(host, port)


def connected():
    return _tecutil_connector.connected


def disconnect():
    _tecutil_connector.disconnect()
