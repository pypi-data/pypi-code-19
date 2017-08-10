__version__ = '0.1.0'

from django.contrib.auth.hashers import make_password


class LogonMixin(object):
    def get_user(self):
        from django.contrib.auth.models import User
        return User.objects.create(
            username='admin',
            password=make_password('password'),
        )

    def setUp(self):
        super(LogonMixin, self).setUp()
        self.user = self.get_user()

        try:  # Django >= 1.9
            self.client.force_login(self.user)
        except AttributeError:
            assert self.client.login(username='admin', password='password')
