import yaml


def load_yaml(path, loader=yaml.SafeLoader):
    """读取并解析 yaml 文件的内容"""
    with open(path) as f:
        return yaml.load(f, loader)


def flatten_dict(d, _parent_path=()):
    """
    将多层级的 dict 抹平，变成单层级的 { path: value } 格式

    {"a": {"b": 1, "c": 2}}  =>  { ("a", "b"): 1, ("a", "c"): 2 }
    """
    flat_dict = {}
    for key, value in d.items():
        path = (*_parent_path, key)
        if isinstance(value, dict):
            flat_dict.update(flatten_dict(value, path))
        else:
            flat_dict[path] = value
    return flat_dict


def deep_set(d, path, value):
    """深入设置 dict 某个下级节点的值，并在目标或中间节点不存在时，将其创建出来"""
    *init, tail = path
    for key in init:
        if key not in d:
            d[key] = {}
        d = d[key]
    d[tail] = value


class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    from tornado.util
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def recursive_object_dict(orig_dict):
    """将 dict 递归转换成 ObjectDict，即下级的所有 dict 也都转换成 ObjectDict）"""
    return ObjectDict({
        key: (recursive_object_dict(value) if isinstance(value, dict) else value)
        for key, value in orig_dict.items()
    })
