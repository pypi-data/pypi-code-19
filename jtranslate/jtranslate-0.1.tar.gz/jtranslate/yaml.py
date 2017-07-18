import random

import yaml


class YamlLoader(yaml.Loader):
    pass


class YamlDumper(yaml.Dumper):
    pass


class TranslateObject:
    yaml_tag = None

    def get_text(self, locale):
        raise NotImplementedError

    @classmethod
    def to_python(cls, loader: YamlLoader, node):
        data = loader.construct_mapping(node)
        return cls(**data)

    def to_yaml(self):
        return self.__dict__

    @staticmethod
    def convert_to_yaml(dumper: YamlDumper, self):
        print(dumper, self)
        node = dumper.represent_mapping(self.yaml_tag, self.to_yaml())
        return node


class RandomVariant(TranslateObject):
    yaml_tag = '!random'

    def __init__(self, variants=None):
        if variants is None:
            variants = []
        self.variants = variants

    def get_text(self, locale):
        if hasattr(self, 'variants'):
            return random.choice(self.variants)


class Joinable(TranslateObject):
    yaml_tag = '!join'

    def __init__(self, elements=None, separator='\n'):
        if elements is None:
            elements = []
        self.elements = elements
        self.separator = separator

    def get_text(self, locale):
        return self.separator.join(self.elements)


def register_type(obj, Loader=YamlLoader, Dumper=YamlDumper):
    tag = obj.yaml_tag
    yaml.add_constructor(tag, obj.to_python, Loader=Loader)
    yaml.add_representer(tag, obj.convert_to_yaml, Dumper=Dumper)


register_type(RandomVariant)
register_type(Joinable)


def dump(data, stream=None, **kwargs):
    return yaml.dump(data, stream, Dumper=YamlDumper, default_flow_style=False, allow_unicode=True,
                     width=1024, indent=2, **kwargs)


def load(stream):
    return yaml.load(stream, Loader=YamlLoader)
