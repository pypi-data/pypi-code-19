import os

from django.core.wsgi import get_wsgi_application

from configfactory.support import dirs


os.environ.setdefault("CONFIGFACTORY_CONFIG", dirs.root_dir('configfactory.dev.yml'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configfactory.settings")

application = get_wsgi_application()
