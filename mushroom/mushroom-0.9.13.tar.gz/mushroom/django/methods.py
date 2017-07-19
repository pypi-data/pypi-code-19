# This module "extends" the basic RPC methods. The following * import
# makes it possible to just import "mushroom.django.rpc" and also have
# access to the basic RPC method classes.
from mushroom.rpc.methods import *


class PaginatedModelListMethod(PaginatedListMethod):
    model_class = None

    def get_objects(self):
        return self.model_class.objects.all()

    def get_object_count(self):
        return self.all_objects.count()
