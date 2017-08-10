from collections import ChainMap
from itertools import chain
from typing import Any, Dict, Iterable, List

from .meta import NamedTuple, member
from .rect import Rect


class WindowProperties(NamedTuple):
    title = member()  # type: str
    class_ = member()  # type: str
    instance = member()  # type: str
    transient_for = member()
    window_role = member()

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> 'WindowProperties':
        d['class_'] = d['class']
        del d['class']
        return WindowProperties(**ChainMap(d, WIN_PROPS_DEFAULTS))


WIN_PROPS_DEFAULTS = dict.fromkeys(WindowProperties._fields(),
                                   None)  # type: Dict[str, Any]


class Container(NamedTuple):
    border = member()  # type :str
    current_border_width = member()  # type: int
    deco_rect = member()  # type: Rect
    floating = member()  # type: str
    floating_nodes = member()  # type: List[Container]
    focus = member()
    focused = member()  # type: bool
    fullscreen_mode = member()  # type: int
    geometry = member()  # type: Rect
    id = member()  # type: int
    last_split_layout = member()  # type: str
    layout = member()  # type: str
    name = member()  # type : str
    nodes = member()  # type: List[Container]
    num = member()
    orientation = member()  # type: str
    output = member()  # type: str
    parent = member()  # type: Container
    percent = member()  # type: float
    rect = member()  # type: Rect
    scratchpad_state = member()  # type: str
    sticky = member()  # type: bool
    swallows = member()
    type = member()  # type: str
    urgent = member()  # type: bool
    window = member()  # type: int
    window_rect = member()  # type: Rect
    window_properties = member()  # type: WindowProperties
    workspace_layout = member()  # type: str

    def __repr__(self):
        return _container_repr(self)

    @property
    def all_nodes(self) -> Iterable['Container']:
        return chain(self.nodes, self.floating_nodes)

    def search(self, pred) -> List['Container']:
        found = []

        if pred(self):
            found.append(self)

        for node in self.all_nodes:
            found.extend(node.search(pred))

        return found

    def search_property(self, **kwargs) -> List['Container']:
        def predicate(c):
            return all(getattr(c, k) == v for k, v in kwargs.items())
        return self.search(predicate)

    def search_any_property(self, **kwargs) -> List['Container']:
        def predicate(c):
            return any(getattr(c, k) == v for k, v in kwargs.items())
        return self.search(predicate)

    def workspace(self) -> 'Container':
        container = self

        while container is not None:
            if container.type == 'workspace':
                return container
            container = container.parent

    def root(self) -> 'Container':
        container = self

        while container is not None:
            if container.parent is None:
                return container
            container = container.parent

    @staticmethod
    def from_dict(d: Dict[str, Any], parent=None) -> 'Container':
        d['deco_rect'] = Rect(**d['deco_rect'])
        d['geometry'] = Rect(**d['geometry'])
        d['rect'] = Rect(**d['rect'])
        d['window_rect'] = Rect(**d['window_rect'])

        if 'window_properties' in d:
            d['window_properties'] = (
                WindowProperties.from_dict(d['window_properties']))
        else:
            d['window_properties'] = WindowProperties('', '', '', '', '')

        nodes = d['nodes']
        floating_nodes = d['floating_nodes']

        d['nodes'] = []
        d['floating_nodes'] = []
        d['parent'] = parent

        c = Container(**ChainMap(d, DEFAULTS))

        c.nodes.extend(Container.from_dict(subd, c) for subd in nodes)
        c.floating_nodes.extend(Container.from_dict(subd, c)
                                for subd in floating_nodes)

        return c


DEFAULTS = dict.fromkeys(Container._fields(), None)  # type: Dict[str, Any]

_CONTAINER_REPR_FIELDS = ', '.join(
    '{}={{{}!r}}'.format(f, fn)
    for fn, f in enumerate(Container._fields())
    if f != 'parent')


def _container_repr(c):
    return '{}({})'.format(c.__class__.__name__,
                           _CONTAINER_REPR_FIELDS.format(*c))
