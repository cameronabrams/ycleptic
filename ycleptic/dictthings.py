# Author: Cameron F. Abrams <cfa22@drexel.edu>

"""
Utilities for modifying dictionary entries in the directive tree
"""

import logging
logger=logging.getLogger(__name__)

def special_update(dict1,dict2):
    """
    Updates dict1 with values from dict2 in a "special" way so that
    any list values are appended rather than overwritten

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
    for k,v in dict2.items():
        ov=dict1.get(k,None)
        if not ov:
            dict1[k]=v
        else:
            if type(v)==list and type(ov)==list:
                logger.debug(f'merging {v} into {ov}')
                for nv in v:
                    if not nv in ov:
                        logger.debug(f'appending {nv}')
                        ov.append(nv)
            elif type(v)==dict and type(ov)==dict:
                ov.update(v)
            else:
                dict1[k]=v # overwrite
    return dict1

