import amino.test.spec_spec

from golgi import Config

Config.enable_lazy_class_attr = False


class SpecConfigConcern:

    def setup(self, configs=['golgi'], allow_files=False, *a, **kw):
        super().setup(*a, **kw)
        Config.allow_files = allow_files
        Config.setup(*configs, files=allow_files)
        Config.override('general', debug=True)


class Spec(SpecConfigConcern, amino.test.spec_spec.Spec):
    pass

__all__ = ('SpecConfigConcern',)
