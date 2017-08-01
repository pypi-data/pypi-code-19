from django_q.conf import Conf


class ORMBrokerRouter(object):

    def db_for_read(self, model, **hints):

        if model._meta.app_label == "django_q":
            return Conf.ORM
        else:
            return None

    def db_for_write(self, model, **hints):

        if model._meta.app_label == "django_q":
            return Conf.ORM
        else:
            return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):

        if app_label == "django_q" and db == Conf.ORM:
            return True
        else:
            return None
