from django.conf.urls import url
from django.contrib.staticfiles.views import serve


class ValidateLoading(object):
    dependencies = [
        'rest_framework',
    ]

    def validate_dependencies(self):
        uninstalled = []
        for dependency in self.dependencies:
            try:
                __import__(dependency)
            except ImportError:
                uninstalled += [dependency]
        if uninstalled:
            return ('\n!!!!! error required dependencies for easy_rest not installed\n'
                    '{}, consider installing them by: '
                    'pip\n').format(','.join(uninstalled))

    def validate(self):
        error = self.validate_dependencies()
        if error:
            print(error)


ValidateLoading().validate()

urlpatterns = [
    url(r'^static/(?P<path>.*)$', serve),
]
