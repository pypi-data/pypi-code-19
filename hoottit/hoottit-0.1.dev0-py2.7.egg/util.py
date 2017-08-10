"""This module is a collection of helper function used by the other pars of the
application
"""

# standard library
import platform


def send_null_once(decoratee):
    """Advance the generator returned by f once (send null)

    In Python a consumer generator starts at the top of the function body,
    and must be advanced once before being able to consume any data. Please see
    PEP 342 for more details -
    https://www.python.org/dev/peps/pep-0342/#new-generator-method-send-value
    """
    def decorated(*args, **kwargs):
        """Advances the result of the decoratee by one (sends one None)."""
        generator = decoratee(*args, **kwargs)
        next(generator)
        return generator
    return decorated


def make_user_agent(version, sitename):
    """Generate a User-Agent identifier string.

    This custom generated string is used by Reddit to identify clients. Our
    includes the platform on which the script is ran on, the name of the client
    (defined in praw.ini), and the ID of the application. We also added the
    author as a way of contact.
    """
    return ('{sitename}-{system}:'
            'com.hootsuite.hoottit:'
            'v{version} (by /u/owlree)').format(sitename=sitename,
                                                version=version,
                                                system=platform.system())


def pipe(source, destination, through=lambda x: x):
    """Create and return a callable object that pipes the source to the
    destination

    This function returns a callable object f that when executed takes data
    from the source and sends it to the destination through a specified
    function that defaults to identity.
    """
    def pipe_executor():
        """Takes data from source and sends it to the destination."""
        for obj in source:
            destination.send(through(obj))
    return pipe_executor


def remove_parameters(url):
    """Remove query parameters from a URL.

    This function looks for a '?' and removes it, together with everything that
    comes after. It also removes the trailing slash in order to keep things
    clean.
    """
    pos = url.find('?')
    if pos > -1:
        url = url[:pos]
    if url[-1] == '/':
        url = url[:-1]
    return url


def execute(some_callable):
    """Really simple functio that calls its argument."""
    some_callable()
