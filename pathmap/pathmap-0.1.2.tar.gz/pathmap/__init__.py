# -*- coding: utf-8 -*-
from .pathmap import (
    clean_path,
    _check_ancestors,
    _resolve_path,
    resolve_paths,
    resolve_by_method
)

from .utils import (
    _extract_match
)

from .tree import Tree


__version__ = '0.1.2'
