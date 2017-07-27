__all__ = ['SetConfigMixin']


class SetConfigMixin:
    @staticmethod
    def SetConfig(app, **confs):
        app.config.SQLDBURLS = confs
        return app
