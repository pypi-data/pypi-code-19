from opfront.model import Model
from opfront.resource import OpfrontResource


class ProductResource(OpfrontResource):

    def _make_model(self, **args):
        model = super()._make_model(**args)
        if getattr(model, 'spectacle', None):
            model.spectacle = Model(OpfrontResource('/spectacles', self._client), **model.spectacle)

        return model
