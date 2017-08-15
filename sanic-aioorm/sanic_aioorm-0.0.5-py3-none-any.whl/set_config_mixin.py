__all__ = ['SetConfigMixin']


class SetConfigMixin:
    @staticmethod
    def SetConfig(app, **confs):
        """设置app的SQLDBURLS设置字段
        """
        app.config.SQLDBURLS = confs
        return app
