#-----------------------------------------------------------------------------
# Copyright (c) Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------
''' Functions useful for generating rich sphinx links for properties

'''

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import annotations

import logging # isort:skip
from typing import Dict

log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import Any, Callable, TypeAlias

_type_links: Dict[type[Any], Callable[[Any], str]] = {}

_property_link_cache: Dict[type[Any], str] = {}

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

__all__ = (
    'model_link',
    'property_link',
    'register_type_link',
    'type_link',
)

_type_links: dict[type[Any], Callable[[Any], str]] = {}

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

def model_link(fullname: str) -> str:
    # (double) escaped space at the end is to appease Sphinx
    # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#gotchas
    return f":class:`~{fullname}`\\ "

def property_link(obj: Any) -> str:
    # (double) escaped space at the end is to appease Sphinx
    # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#gotchas
    obj_type = type(obj)
    if obj_type in _property_link_cache:
        return _property_link_cache[obj_type]
    result = f":class:`~bokeh.core.properties.{obj_type.__name__}`\\ "
    _property_link_cache[obj_type] = result
    return result

Fn: TypeAlias = Callable[[Any], str]

def register_type_link(cls: type[Any]) -> Callable[[Fn], Fn]:
    def decorator(func: Fn):
        _type_links[cls] = func
        return func
    return decorator

def type_link(obj: Any) -> str:
    obj_type = type(obj)
    return _type_links.get(obj_type, property_link)(obj)

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
