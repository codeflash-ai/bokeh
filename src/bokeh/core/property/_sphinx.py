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
log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
from typing import Any, Callable, TypeAlias

_property_link_cache: dict[type[Any], str] = {}

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
    obj_class = obj.__class__
    if obj_class in _property_link_cache:
        return _property_link_cache[obj_class]
    
    # (double) escaped space at the end is to appease Sphinx
    # https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#gotchas
    result = f":class:`~bokeh.core.properties.{obj_class.__name__}`\\ "
    _property_link_cache[obj_class] = result
    return result

Fn: TypeAlias = Callable[[Any], str]

def register_type_link(cls: type[Any]) -> Callable[[Fn], Fn]:
    def decorator(func: Fn):
        _type_links[cls] = func
        return func
    return decorator

def type_link(obj: Any) -> str:
    return _type_links.get(obj.__class__, property_link)(obj)

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
