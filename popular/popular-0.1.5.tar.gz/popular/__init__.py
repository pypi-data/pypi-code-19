"""Popular

This package is a minimalist take on social authentication. It focuses
on the OAuth process as two main steps.

    1) Request permission from a user on a service.
        - IN: service name, application secret, etc
        - OUT: string URL
    2) Request auth tokens from a service on behalf of a user.
        - IN: string URL
        - OUT: tokens, user info, etc

This package stays out of the implementation and focuses on the
interaction with the social auth provider.
"""

__license__ = 'MIT License'
__version__ = '0.1.5'


from .manager import Manager as Popular
