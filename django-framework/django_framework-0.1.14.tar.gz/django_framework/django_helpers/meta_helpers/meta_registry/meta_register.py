instance = None

from django_framework.django_helpers.register_helpers import Registry

class MetaRegistry(Registry):
    REGISTRY_TYPE = 'Meta'
    REGISTER = {}
    
    SHOULD_CHECK_TYPE = True
    
    @classmethod
    def set_instance(cls):
        if instance == None:
            global instance
            instance = MetaRegistry()


def register_meta(cls):
    MetaRegistry.set_instance()
    instance.register(cls = cls)

def get_meta(meta_name): # converts string to cls
    return instance.get(name = meta_name)
    
def get_meta_name(meta): # converts cls to a string
    return instance.get_name(cls = meta)

def get_meta_name_list(): # converts cls to a string
    return instance.get_name_list()


# 
# registry = {}
# 
# def register_meta(cls):
#     class_name = cls.__name__
#     if registry.get(class_name) == None:
#         registry[class_name] = cls
#     else:
#         raise NameError('The class you are trying to register is already in!...')
#     
#     
# def get_meta(meta = None, meta_name = None, model = None):
# 
#     if model:
#         manager = model + 'Meta'
#     elif meta_name:
#         manager = model
# 
# 
#     model = registry.get(manager) 
#     if model == None:
#         raise AttributeError('You have not properly registered this model name, or this name does not exist.')
#     
#     return model

