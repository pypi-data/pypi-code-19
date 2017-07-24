

class MeaspkViewSetMixin(object):

    def initial(self, request, *args, **kwargs):
        if kwargs.get('pk') == 'me':
            kwargs['pk'] = request.user.pk

        for k, v in kwargs.items():
            if k.startswith('parent_lookup_') and v == 'me':
                kwargs[k] = request.user.pk

        self.kwargs = kwargs

        super(MeaspkViewSetMixin, self).initial(request, *args, **kwargs)


class ActionSerializerViewSetMixin(object):

    serializer_classes = None

    def get_serializer_class(self):
        if hasattr(self, 'serializer_classes') and isinstance(self.serializer_classes, dict):
            serializer_class = self.serializer_classes.get(self.action)

            if serializer_class:
                return serializer_class

        return super(ActionSerializerViewSetMixin, self).get_serializer_class()

    def get_permissions(self):
        if hasattr(self, 'permission_classes') and isinstance(self.permission_classes, dict):
            permissions = self.permission_classes.get(self.action)

            if permissions:
                return [permission() for permission in permissions]
            else:
                return ()
        else:
            return super(ActionSerializerViewSetMixin, self).get_permissions()
