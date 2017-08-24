from defaults import *

SECRET_KEY = 'Wz;tJ]^&-IQ8IgNzkDU<I@L`{g7$r%{8.LLG]oG?`d,y1[eos::pbFoO8wsI|O@J/rTXaD9BII[#[;!vYXHwn=aO;d9\T*B{@guK'

DEBUG = False

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.production.sqlite3'),
    }
}

### LDAP AUTHENTICATION ###

import ldap
import django_auth_ldap.backend
from django.dispatch.dispatcher import Signal, receiver

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}
AUTH_LDAP_SERVER_URI = "ldaps://localhost:9000"
AUTH_LDAP_USER_DN_TEMPLATE = "uid=%(user)s,ou=people,dc=uchicago,dc=edu"

AUTH_LDAP_USER_ATTR_MAP = {
    "first_name": "givenName",
    "last_name": "sn",
    "email": "mail"
}

CHISUBMIT_ADMINS = ["borja", "chudler"]
CHISUBMIT_ADMINS_DNS = [AUTH_LDAP_USER_DN_TEMPLATE % {"user": u} for u in CHISUBMIT_ADMINS]

@receiver(django_auth_ldap.backend.populate_user)
def ldap_user_create_callback(sender, **kwargs):
    user = kwargs["user"]
    ldap_user = kwargs["ldap_user"]
    if ldap_user.dn in CHISUBMIT_ADMINS_DNS:
        user.is_staff = True
        user.is_superuser = True
        user.save()

if DEBUG:
    import logging
    
    logger = logging.getLogger('django_auth_ldap')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)