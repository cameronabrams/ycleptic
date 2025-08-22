# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Utilities for modifying dictionary entries in the directive tree
"""

import logging
logger = logging.getLogger(__name__)

def special_update(dict1: dict, dict2: dict):
    """
    Updates dict1 with values from dict2 in a "special" way so that
    any values that are list-like are appended rather than overwritten,
    and dict-like values are updated.
    For each key:value pair in dict2,
       - if the value is a list and the existing value at key in dict1 is also a list, append the dict2 values to dict1
       - if the value is a dict and the existing value is also a dict, merge them
       - otherwise, overwrite the existing value

    Parameters
    ----------
    dict1 : dict
        The dictionary to be updated.
    dict2 : dict
        The dictionary with values to update dict1.

    Returns
    -------
    dict
        The updated dict1 with values from dict2 merged in.
    """
    for k, v in dict2.items():
        ov = dict1.get(k, None)
        if not ov:
            dict1[k] = v
        else:
            if type(v) == list and type(ov) == list:
                for nv in v:
                    if not nv in ov:
                        ov.append(nv)
            elif type(v) == dict and type(ov) == dict:
                ov.update(v)
            else:
                dict1[k] = v  # overwrite
    return dict1

