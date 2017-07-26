from opfront.model import Model
from opfront.resource import OpfrontResource


class StoreResource(OpfrontResource):

    def _make_model(self, **args):
        model = super()._make_model(**args)
        if getattr(model, 'banner', None) is not None:
            model.banner = Model(OpfrontResource('/banners', self._client), **model.banner)

        return model
