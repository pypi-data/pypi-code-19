from provider import Provider

class AbstractFactory():
    def __init__(self):
        self.factories = {}

    def set(self, factory):
        instance = factory()

        if not hasattr(instance, 'interface_type'):
            raise ValueError('factory requires provider/interface type')

        self.factories[instance.interface_type] = factory

    def remove(self, factory):
        self.factories.remove(factory)

    def resolve(self, provider, *args, **kwargs):
        interface_type = type(provider)

        if interface_type not in self.factories:
            return None

        factory = self.factories[interface_type]

        if factory is None:
            return None

        return factory().create(*args, **kwargs) 