from opfront.model import Model
from opfront.resource import OpfrontResource


class OrderResource(OpfrontResource):

    def _make_model(self, **args):
        model = super()._make_model(**args)
        if getattr(model, 'products', None):
            model.products = [Model(OpfrontResource('/products', self._client), **prod) for prod in model.products]

        if getattr(model, 'store', None):
            model.store = Model(OpfrontResource('/stores', self._client), **model.store)

        return model
