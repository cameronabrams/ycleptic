# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Utilities for modifying dictionary entries in the Attribute tree
"""

from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


def special_update(dict1: dict, dict2: dict, list_mode: str = 'append'):
    """
    Updates dict1 with values from dict2 in a "special" way so that
    any values that are list-like are merged rather than overwritten,
    and dict-like values are updated.
    For each key:value pair in dict2,

       - if the value is a list and the existing value at key in dict1 is also a list, merge them according to ``list_mode``
       - if the value is a dict and the existing value is also a dict, merge them
       - otherwise, overwrite the existing value

    Parameters
    ----------
    dict1 : dict
        The dictionary to be updated.
    dict2 : dict
        The dictionary with values to update dict1.
    list_mode : str, optional
        How a list in ``dict2`` combines with a list already at the same key in
        ``dict1``.  ``'append'`` (the default) is ycleptic's historical
        behavior: values not already present are added, **keeping dict1's
        ordering**, so a caller's list is interleaved into the existing one
        rather than following it.  ``'replace'`` discards the existing list and
        takes dict2's verbatim, which is the only way to preserve the caller's
        own ordering.

        The mode governs only lists at this level.  A nested dict is still
        merged with a plain ``update``, which overwrites a list deeper down
        under either mode -- longstanding behavior that is left alone here
        rather than quietly corrected, since downstream base configs are
        written against it.

    Returns
    -------
    dict
        The updated dict1 with values from dict2 merged in.
    """
    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = v
            continue
        ov = dict1[k]
        if isinstance(v, list) and isinstance(ov, list):
            if list_mode == 'replace':
                dict1[k] = v
            else:
                for nv in v:
                    if nv not in ov:
                        ov.append(nv)
        elif isinstance(v, dict) and isinstance(ov, dict):
            ov.update(v)
        else:
            dict1[k] = v  # overwrite
    return dict1
