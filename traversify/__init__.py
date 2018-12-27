"""
traversify
~~~~~~~~~~~

:copyright: (c) 2018 Alan Elkner (aelkner@gmail.com)
:license: GNU GENERAL PUBLIC LICENSE version 3, see LICENSE for more details.

"""

from .traverser import Traverser, Filter, ensure_list, is_identifier
from .metadata import (
    __author__,
    __copyright__,
    __email__,
    __license__,
    __maintainer__,
    __version__,
)

_all__ = [
    '__author__', '__copyright__', '__email__', '__license__',
    '__maintainer__', '__version__', 'Traverser',
]