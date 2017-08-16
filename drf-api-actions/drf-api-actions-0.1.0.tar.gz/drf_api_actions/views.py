from rest_framework.schemas import SchemaGenerator


class ActionReadMixin(object):
    """
    让coreapi schema生成的时候，识别出来的action为"read"（而不是 "list"）
    """

    @classmethod
    def as_view(cls, **initkwargs) -> object:
        view = super(ActionReadMixin, cls).as_view(**initkwargs)
        view.actions = {'get': 'retrieve'}
        return view


class SchemaGeneratorEx(SchemaGenerator):
    def has_view_permissions(self, path, method, view):  # 需要登录的API也列出来
        return True

    def get_filter_fields(self, path, method, view):
        filters = super(SchemaGeneratorEx, self).get_filter_fields(path, method, view)
        filters += self.get_extra_fields(path, method, view)
        return filters

    def get_extra_fields(self, path, method, view):
        return getattr(view, 'extra_fields', [])
