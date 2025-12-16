#-----------------------------------------------------------------------------
# Copyright (c) Anaconda, Inc., and Bokeh Contributors.
# All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Boilerplate
#-----------------------------------------------------------------------------
from __future__ import annotations

import logging # isort:skip
from bokeh.core.property.vectorization import field
from bokeh.models import Circle, ColumnDataSource, ColumnarDataSource, GlyphRenderer, MultiLine, Scatter
from bokeh.plotting._renderer import make_glyph, pop_visuals

log = logging.getLogger(__name__)

#-----------------------------------------------------------------------------
# Imports
#-----------------------------------------------------------------------------

# Standard library imports
import sys

# Bokeh imports
from ..core.property.vectorization import field
from ..models import (
    Circle,
    ColumnarDataSource,
    ColumnDataSource,
    GlyphRenderer,
    MultiLine,
    Scatter,
)
from ._renderer import make_glyph, pop_visuals

#-----------------------------------------------------------------------------
# Globals and constants
#-----------------------------------------------------------------------------

__all__ = (
    'get_graph_kwargs'
)

RENDERER_ARGS = ['name', 'level', 'visible', 'x_range_name', 'y_range_name',
                 'selection_policy', 'inspection_policy']

#-----------------------------------------------------------------------------
# General API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Dev API
#-----------------------------------------------------------------------------

def get_graph_kwargs(node_source: ColumnDataSource, edge_source: ColumnDataSource, **kwargs) -> dict:

    if not isinstance(node_source, ColumnarDataSource):
        try:
            node_source = ColumnDataSource(node_source)
        except ValueError as err:
            msg = f"Failed to auto-convert {type(node_source)} to ColumnDataSource.\n Original error: {err}"
            raise ValueError(msg).with_traceback(sys.exc_info()[2])

    if not isinstance(edge_source, ColumnarDataSource):
        try:
            edge_source = ColumnDataSource(edge_source)
        except ValueError as err:
            msg = f"Failed to auto-convert {type(edge_source)} to ColumnDataSource.\n Original error: {err}"
            raise ValueError(msg).with_traceback(sys.exc_info()[2])

    marker = kwargs.pop('node_marker', None)
    marker_type = Scatter
    node_data = node_source.data
    # Avoid multiple lookups for isinstance(dict, ...) and marker in data during workflow
    marker_is_field = (isinstance(marker, dict) and 'field' in marker) or marker in node_data
    if marker_is_field:
        kwargs['node_marker'] = field(marker)
    else:
        if isinstance(marker, dict) and 'value' in marker:
            marker = marker['value']

        if marker is None or marker == "circle":
            if "node_radius" in kwargs:
                marker_type = Circle
            else:
                marker_type = Scatter
        else:
            kwargs["node_marker"] = marker

    # Precompute sets and key lists to avoid multiple .copy()/.items() fetches
    marker_type_props = marker_type.properties()
    multiln_props = MultiLine.properties()

    # Use list comprehensions for fast property extraction, not repeated copy
    node_kwargs = {k.lstrip('node_'): v for k, v in kwargs.items() if k.startswith('node_') and k.lstrip('node_') in marker_type_props}
    edge_kwargs = {k.lstrip('edge_'): v for k, v in kwargs.items() if k.startswith('edge_') and k.lstrip('edge_') in multiln_props}

    ## node stuff
    node_visuals = pop_visuals(marker_type, kwargs, prefix="node_")

    # Reduce multiple key scans to a single efficient loop
    snode_visuals = None
    hnode_visuals = None
    found_sel = False
    found_hover = False
    for k in kwargs:
        if not found_sel and k.startswith('node_selection_'):
            snode_visuals = pop_visuals(marker_type, kwargs, prefix="node_selection_", defaults=node_visuals)
            found_sel = True
        if not found_hover and k.startswith('node_hover_'):
            hnode_visuals = pop_visuals(marker_type, kwargs, prefix="node_hover_", defaults=node_visuals)
            found_hover = True
        if found_sel and found_hover:
            break

    if snode_visuals is None:
        snode_visuals = None
    if hnode_visuals is None:
        hnode_visuals = None

    mnode_visuals = pop_visuals(marker_type, kwargs, prefix="node_muted_", defaults=node_visuals, override_defaults={'alpha':0.2})
    nsnode_visuals = pop_visuals(marker_type, kwargs, prefix="node_nonselection_", defaults=node_visuals)

    ## edge stuff
    edge_visuals = pop_visuals(MultiLine, kwargs, prefix="edge_")

    sedge_visuals = None
    hedge_visuals = None
    found_sel = False
    found_hover = False
    for k in kwargs:
        if not found_sel and k.startswith('edge_selection_'):
            sedge_visuals = pop_visuals(MultiLine, kwargs, prefix="edge_selection_", defaults=edge_visuals)
            found_sel = True
        if not found_hover and k.startswith('edge_hover_'):
            hedge_visuals = pop_visuals(MultiLine, kwargs, prefix="edge_hover_", defaults=edge_visuals)
            found_hover = True
        if found_sel and found_hover:
            break

    if sedge_visuals is None:
        sedge_visuals = None
    if hedge_visuals is None:
        hedge_visuals = None

    medge_visuals = pop_visuals(MultiLine, kwargs, prefix="edge_muted_", defaults=edge_visuals, override_defaults={'alpha':0.2})
    nsedge_visuals = pop_visuals(MultiLine, kwargs, prefix="edge_nonselection_", defaults=edge_visuals)

    ## node stuff
    node_glyph = make_glyph(marker_type, node_kwargs, node_visuals)
    nsnode_glyph = make_glyph(marker_type, node_kwargs, nsnode_visuals)
    snode_glyph = make_glyph(marker_type, node_kwargs, snode_visuals)
    hnode_glyph = make_glyph(marker_type, node_kwargs, hnode_visuals)
    mnode_glyph = make_glyph(marker_type, node_kwargs, mnode_visuals)

    node_renderer = GlyphRenderer(
        data_source=node_source,
        glyph=node_glyph,
        selection_glyph=snode_glyph or "auto",
        nonselection_glyph=nsnode_glyph or "auto",
        hover_glyph=hnode_glyph,
        muted_glyph=mnode_glyph or "auto",
    )

    ## edge stuff
    edge_glyph = make_glyph(MultiLine, edge_kwargs, edge_visuals)
    nsedge_glyph = make_glyph(MultiLine, edge_kwargs, nsedge_visuals)
    sedge_glyph = make_glyph(MultiLine, edge_kwargs, sedge_visuals)
    hedge_glyph = make_glyph(MultiLine, edge_kwargs, hedge_visuals)
    medge_glyph = make_glyph(MultiLine, edge_kwargs, medge_visuals)

    edge_renderer = GlyphRenderer(
        data_source=edge_source,
        glyph=edge_glyph,
        selection_glyph=sedge_glyph or "auto",
        nonselection_glyph=nsedge_glyph or "auto",
        hover_glyph=hedge_glyph,
        muted_glyph=medge_glyph or "auto",
    )

    # Extract renderer kwargs directly, no repeated lookup
    renderer_kwargs = {attr: kwargs.pop(attr) for attr in RENDERER_ARGS if attr in kwargs}

    renderer_kwargs["node_renderer"] = node_renderer
    renderer_kwargs["edge_renderer"] = edge_renderer

    return renderer_kwargs

#-----------------------------------------------------------------------------
# Private API
#-----------------------------------------------------------------------------

#-----------------------------------------------------------------------------
# Code
#-----------------------------------------------------------------------------
